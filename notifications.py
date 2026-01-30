import requests
import config

class TelegramNotifier:
    """
    Sends alerts to Telegram.
    Uses config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID.
    """
    BASE_URL = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"

    def send_alert(self, message):
        """Sends a plain text message."""
        if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
            try:
                print(f"TELEGRAM (Mock): {message}")
            except UnicodeEncodeError:
                print(f"TELEGRAM (Mock): {message.encode('utf-8')}")
            return

        payload = {
            "chat_id": config.TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            requests.post(self.BASE_URL, json=payload, timeout=5)
        except Exception as e:
            print(f"Failed to send Telegram alert: {e}")

    def send_recommendation(self, symbol, action, quantity, price, stop_loss=None, target_price=None):
        """Sends a structured BUY/SELL recommendation."""
        icon = "[BUY]" if action == "BUY" else "[SELL]"
        sl_text = f"\n[SL] Stop Loss: {stop_loss}" if stop_loss else ""
        tp_text = f"\n[TP] Target: {target_price} (Tax-Adjusted)" if target_price else ""
        
        msg = (
            f"{icon} *ADVISORY ALERT*\n"
            f"Symbol: `{symbol}`\n"
            f"Action: *{action}*\n"
            f"Quantity: *{quantity}*\n"
            f"Price: {price}"
            f"{sl_text}"
            f"{tp_text}\n"
            f"-------------------\n"
            f"Risk: 1% of Capital\n\n"
            f"Details: [Tap to Open Dashboard]({config.PUBLIC_DASHBOARD_URL})"
        )
        self.send_alert(msg)
