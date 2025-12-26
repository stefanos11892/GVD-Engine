from src.agents.radar import RadarAgent

def run_radar_chain(focus):
    logs = []
    def log(msg):
        print(msg)
        logs.append(str(msg))

    log(f"--- Starting News Radar Chain ---")
    log(f"Focus Area: {focus}")
    
    radar = RadarAgent()
    log("\n@Radar is scanning the horizon...")
    
    context_data = ""
    if focus == "all":
        try:
            from src.utils.data_manager import data_manager
            tickers = data_manager.get_holdings_list()
            if tickers:
                context_data = f"Active Portfolio Holdings: {', '.join(tickers)}"
                log(f"Loaded {len(tickers)} tickers from DataManager.")
            else:
                log("WARNING: No holdings found in DataManager.")
        except Exception as e:
            log(f"ERROR reading portfolio: {e}")
    
    prompt = f"Scan for material news events regarding '{focus}'. Focus on risks and negative catalysts."
    radar_output = radar.run(prompt, context=context_data)
    
    log(f"Radar Report:\n{radar_output}\n")
    
    return "\n".join(logs)
