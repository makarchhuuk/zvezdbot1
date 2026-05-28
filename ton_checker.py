import aiohttp
import asyncio
from datetime import datetime, timedelta

class TonChecker:
    def __init__(self, wallet_address):
        self.wallet = wallet_address
        self.base_url = "https://toncenter.com/api/v3/"
        self.last_check = None
    
    async def check_transactions(self, comment=None):
        """Проверяет последние входящие транзакции"""
        url = f"{self.base_url}transactions?account={self.wallet}&limit=20"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as resp:
                    data = await resp.json()
                    
                    if "transactions" not in data:
                        return []
                    
                    transactions = []
                    for tx in data["transactions"]:
                        # Проверяем входящие транзакции
                        if tx.get("in_msg", {}).get("destination") == self.wallet:
                            msg = tx.get("in_msg", {})
                            amount = msg.get("value", 0) / 1_000_000_000  # nanoTON -> TON
                            comment_raw = msg.get("decoded_body", {}).get("text", "") or msg.get("comment", "")
                            
                            transactions.append({
                                "amount": amount,
                                "comment": comment_raw,
                                "hash": tx.get("hash", ""),
                                "timestamp": tx.get("utime", 0)
                            })
                    return transactions
            except Exception as e:
                print(f"Ошибка проверки транзакций: {e}")
                return []
    
    async def wait_for_payment(self, expected_comment, timeout_seconds=300, check_interval=15):
        """Ждёт оплату с указанным комментарием"""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout_seconds:
            txs = await self.check_transactions()
            
            for tx in txs:
                if expected_comment.lower() in tx["comment"].lower():
                    return tx
            
            await asyncio.sleep(check_interval)
        
        return None