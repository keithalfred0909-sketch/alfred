//+------------------------------------------------------------------+
//| NQ_ORB5_v2_DemoOnly.mq5                                          |
//| X-QUANT strategy nq_orb5_v2, variant A (no context filter):      |
//| 5-minute opening-range breakout on the Nasdaq 100 / NQ.          |
//|                                                                  |
//| DEMO / STRATEGY TESTER ONLY. The EA refuses to run on a real     |
//| account (project rule: no real trading before independent        |
//| validation). This is research code, not investment advice.      |
//|                                                                  |
//| Rules (configs/strategies/nq_orb5_v2.yaml):                      |
//|  1 Context  : US cash session days (09:30-16:00 New York)        |
//|  2 Setup    : first 5-min candle 09:30-09:35 NY, body >= 10% of  |
//|               its range; bullish -> long, bearish -> short       |
//|  3 Entry    : market order at 09:35:00 NY (max delay input)      |
//|  4 Stop     : opposite extreme of the opening candle             |
//|  5 Target   : 10R; otherwise close at 16:00 NY                   |
//|  6 Risk     : 1% equity per trade, notional <= 4x equity,        |
//|               daily loss limit 2%                                |
//|  7 No trade : doji, stop < 0.03% of price, incomplete opening    |
//|               candle, known US half days                         |
//| MT5 bars are stamped at their OPEN time: the opening candle is   |
//| the M1 bars opened 09:30..09:34 NY; entry = 09:35:00 NY.         |
//+------------------------------------------------------------------+
#property copyright "X-QUANT research lab"
#property version   "2.00"

#include <Trade\Trade.mqh>

input double InpRiskPercent       = 1.0;    // risk per trade (% of equity)
input double InpDailyLossPercent  = 2.0;    // daily loss limit (% of day-start equity)
input double InpMaxNotionalX      = 4.0;    // max notional as a multiple of equity
input double InpMinBodyFrac       = 0.10;   // min candle body / range
input double InpTargetR           = 10.0;   // take profit in R
input double InpMinStopFrac       = 0.0003; // min stop distance as a fraction of price
input int    InpServerMinusNY     = 7;      // broker server time minus New York time, in hours (7 = "NY close" brokers)
input int    InpMaxEntryDelaySec  = 30;     // skip the day if the 09:35:00 entry cannot be sent within this delay
input long   InpMagic             = 50520260;
input bool   InpWriteJournal      = true;   // CSV journal in MQL5/Files (for the trading diary)

CTrade   trade;
int      g_trade_day   = 0;      // NY yyyymmdd of the last entry attempt (one trade per day)
int      g_equity_day  = 0;      // NY yyyymmdd of the stored day-start equity
double   g_day_equity  = 0.0;
bool     g_day_blocked = false;  // daily loss limit reached

//--- New York time from the trade server time (works in the Strategy Tester, where TimeGMT() is not real GMT)
datetime NYTime() { return TimeTradeServer() - (datetime)(InpServerMinusNY * 3600); }
int      YMD(const MqlDateTime &t) { return t.year * 10000 + t.mon * 100 + t.day; }
datetime ServerFromNY(const datetime ny) { return ny + (datetime)(InpServerMinusNY * 3600); }

//--- known US early-close days (cash 13:00 / futures 13:15 NY): the backtest had no 16:00 bar -> no trade
bool IsHalfDay(const MqlDateTime &t)
  {
   if(t.mon == 12 && t.day == 24) return true;
   if(t.mon == 7 && t.day == 3)   return true;
   // Friday after Thanksgiving (4th Thursday of November falls on the 22nd..28th)
   if(t.mon == 11 && t.day_of_week == 5 && t.day >= 23 && t.day <= 29) return true;
   return false;
  }

void Journal(const string what)
  {
   Print("[NQ_ORB5] ", what);
   if(!InpWriteJournal) return;
   int h = FileOpen("NQ_ORB5_journal.csv", FILE_READ | FILE_WRITE | FILE_CSV | FILE_SHARE_READ | FILE_ANSI, ';');
   if(h == INVALID_HANDLE) return;
   FileSeek(h, 0, SEEK_END);
   FileWrite(h, TimeToString(NYTime(), TIME_DATE | TIME_SECONDS), what);
   FileClose(h);
  }

bool OurPosition(ulong &ticket)
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong tk = PositionGetTicket(i);
      if(tk > 0 && PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == InpMagic)
        { ticket = tk; return true; }
     }
   return false;
  }

//--- realised + floating P&L of this EA since the NY day started
double DayPnL(const datetime ny_day_start)
  {
   double pnl = 0.0;
   if(HistorySelect(ServerFromNY(ny_day_start), TimeTradeServer() + 60))
     {
      for(int i = HistoryDealsTotal() - 1; i >= 0; i--)
        {
         ulong d = HistoryDealGetTicket(i);
         if(HistoryDealGetInteger(d, DEAL_MAGIC) != InpMagic || HistoryDealGetString(d, DEAL_SYMBOL) != _Symbol) continue;
         pnl += HistoryDealGetDouble(d, DEAL_PROFIT) + HistoryDealGetDouble(d, DEAL_COMMISSION) + HistoryDealGetDouble(d, DEAL_SWAP);
        }
     }
   ulong tk;
   if(OurPosition(tk)) pnl += PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
   return pnl;
  }

int OnInit()
  {
   bool tester = (bool)MQLInfoInteger(MQL_TESTER) || (bool)MQLInfoInteger(MQL_OPTIMIZATION);
   if(!tester && AccountInfoInteger(ACCOUNT_TRADE_MODE) != ACCOUNT_TRADE_MODE_DEMO)
     {
      Alert("NQ_ORB5_v2 is DEMO/TESTER ONLY: refusing to run on a non-demo account.");
      return INIT_FAILED;
     }
   if(InpRiskPercent <= 0 || InpRiskPercent > 2.0)
     { Alert("Risk per trade must be in (0, 2]%."); return INIT_PARAMETERS_INCORRECT; }
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(50);
   if(!tester)
     {  // sanity check of the server offset against the real clock (US DST: NY = GMT-4 summer, GMT-5 winter)
      Print("[NQ_ORB5] server ", TimeToString(TimeTradeServer()), " | NY (from offset) ", TimeToString(NYTime()),
            " | GMT ", TimeToString(TimeGMT()), " - check that the NY time is right before trusting the EA");
     }
   EventSetTimer(1);
   Journal(StringFormat("init %s risk %.2f%% daily %.2f%% target %.1fR serverMinusNY %d",
                        _Symbol, InpRiskPercent, InpDailyLossPercent, InpTargetR, InpServerMinusNY));
   return INIT_SUCCEEDED;
  }

void OnDeinit(const int reason) { EventKillTimer(); }

void OnTimer() { Step(); }
void OnTick()  { Step(); }

void Step()
  {
   datetime ny = NYTime();
   MqlDateTime t; TimeToStruct(ny, t);
   int today = YMD(t);
   int mins  = t.hour * 60 + t.min;
   MqlDateTime d0 = t; d0.hour = 0; d0.min = 0; d0.sec = 0;
   datetime ny_day_start = StructToTime(d0);

   if(g_equity_day != today) { g_equity_day = today; g_day_equity = AccountInfoDouble(ACCOUNT_EQUITY); g_day_blocked = false; }

   ulong tk;
   bool has_pos = OurPosition(tk);

   // 6. daily loss limit: stop trading for the day (closes an open position too)
   if(!g_day_blocked && g_day_equity > 0 && DayPnL(ny_day_start) <= -InpDailyLossPercent / 100.0 * g_day_equity)
     {
      g_day_blocked = true;
      if(has_pos) { trade.PositionClose(tk); Journal("daily loss limit reached: position closed, no more trades today"); }
      else Journal("daily loss limit reached: no more trades today");
      return;
     }

   // 5. time exit at 16:00 NY (and never carry a position overnight)
   if(has_pos)
     {
      datetime opened = (datetime)PositionGetInteger(POSITION_TIME);
      MqlDateTime o; TimeToStruct(opened - (datetime)(InpServerMinusNY * 3600), o);
      if(mins >= 16 * 60 || YMD(o) != today)
        {
         double pnl = PositionGetDouble(POSITION_PROFIT);
         if(trade.PositionClose(tk)) Journal(StringFormat("exit 16:00 NY close, P&L %.2f", pnl));
        }
      return;
     }

   // entry window: 09:35:00 .. 09:35:00 + max delay
   int secs = (t.hour * 3600 + t.min * 60 + t.sec) - (9 * 3600 + 35 * 60);
   if(secs < 0 || secs > InpMaxEntryDelaySec || g_trade_day == today || g_day_blocked) return;
   if(t.day_of_week == 0 || t.day_of_week == 6) return;
   g_trade_day = today;                                    // one decision per day, whatever happens below
   if(IsHalfDay(t)) { Journal("no trade: US early-close day"); return; }

   // 2. opening candle = M1 bars opened 09:30..09:34 NY
   MqlDateTime a = t; a.hour = 9; a.min = 30; a.sec = 0;
   MqlDateTime b = t; b.hour = 9; b.min = 34; b.sec = 0;
   MqlRates r[];
   int n = CopyRates(_Symbol, PERIOD_M1, ServerFromNY(StructToTime(a)), ServerFromNY(StructToTime(b)), r);
   if(n != 5) { Journal(StringFormat("no trade: opening candle incomplete (%d M1 bars)", n)); return; }
   double co = r[0].open, cc = r[4].close, ch = r[0].high, cl = r[0].low;
   for(int i = 1; i < 5; i++) { ch = MathMax(ch, r[i].high); cl = MathMin(cl, r[i].low); }
   double rng = ch - cl;
   if(rng <= 0 || MathAbs(cc - co) < InpMinBodyFrac * rng) { Journal("no trade: doji opening candle"); return; }
   int side = (cc > co) ? 1 : -1;

   // 3-4-5. entry, stop, target
   MqlTick q; if(!SymbolInfoTick(_Symbol, q)) { Journal("no trade: no tick"); return; }
   double entry = (side > 0) ? q.ask : q.bid;
   double stop  = (side > 0) ? cl : ch;
   double dist  = (entry - stop) * side;
   if(dist <= 0) { Journal("no trade: price already beyond the stop"); return; }
   if(dist / entry < InpMinStopFrac) { Journal("no trade: stop too tight"); return; }
   double target = entry + side * InpTargetR * dist;
   long stops_level = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   if(dist < stops_level * _Point) { Journal("no trade: stop closer than the broker's stops level"); return; }

   // 6. size: risk% of equity / loss per lot at the stop, capped by notional
   double tick_size  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double equity     = AccountInfoDouble(ACCOUNT_EQUITY);
   if(tick_size <= 0 || tick_value <= 0) { Journal("no trade: missing tick size/value"); return; }
   double loss_per_lot     = dist / tick_size * tick_value;
   double notional_per_lot = entry / tick_size * tick_value;
   double lots = MathMin(equity * InpRiskPercent / 100.0 / loss_per_lot, InpMaxNotionalX * equity / notional_per_lot);
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), vmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   lots = MathMin(NormalizeDouble(MathFloor(lots / step + 1e-9) * step, 8), vmax);
   if(lots < vmin) { Journal(StringFormat("no trade: 1%% risk is below the minimum volume (%.2f < %.2f)", lots, vmin)); return; }

   stop = NormalizeDouble(stop, _Digits); target = NormalizeDouble(target, _Digits);
   bool ok = (side > 0) ? trade.Buy(lots, _Symbol, 0.0, stop, target, "nq_orb5_v2")
                        : trade.Sell(lots, _Symbol, 0.0, stop, target, "nq_orb5_v2");
   Journal(StringFormat("%s %s lots %.2f entry~%.2f stop %.2f target %.2f risk %.2f%% (%s)",
                        ok ? "ENTRY" : "ORDER FAILED", side > 0 ? "LONG" : "SHORT", lots, entry, stop, target,
                        lots * loss_per_lot / equity * 100.0, ok ? "ok" : trade.ResultRetcodeDescription()));
  }
//+------------------------------------------------------------------+
