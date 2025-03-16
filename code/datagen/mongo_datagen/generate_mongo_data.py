import os
import logging
import random
from datetime import timedelta
from uuid import uuid4
from typing import Dict

from faker import Faker
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from bson.decimal128 import Decimal128

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDataGenerator:
    def __init__(self):
        self.__fake = Faker()
        self.__client = None
        self.__db = None
        self.__user_ids = list(range(1000, 2000))
        self.__product_ids = list(range(1, 501))
        self.__num_user_sessions = int(os.getenv("MONGO_DATAGEN_NUM_USER_SESSIONS"))
        self.__num_event_logs = int(os.getenv("MONGO_DATAGEN_NUM_EVENT_LOGS"))
        self.__num_support_tickets = int(os.getenv("MONGO_DATAGEN_NUM_SUPPORT_TICKETS"))
        self.__num_moderation_queues = int(os.getenv("MONGO_DATAGEN_NUM_MODERATION_QUEUES"))
        self.__num_search_queries = int(os.getenv("MONGO_DATAGEN_NUM_SEARCH_QUERIES"))
        
        self._connect()

    def _connect(self):
        """Установка соединения с MongoDB"""
        try:
            self.__client = MongoClient(
                host=os.getenv("MONGO_HOST", "localhost"),
                port=int(os.getenv("MONGO_PORT", 27017)),
                username=os.getenv("MONGO_USER"),
                password=os.getenv("MONGO_PASSWORD"),
                authSource=os.getenv("MONGO_INITDB_DB")
            )
            self.__db = self.__client[os.getenv("MONGO_INITDB_DB")]
            logger.info("Successfully connected to MongoDB")
        except PyMongoError as e:
            logger.error(f"Connection error: {e}")
            raise

    def _generate_device_info(self) -> Dict:
        """Генерация информации об устройстве"""
        return {
            "type": random.choice(["desktop", "mobile", "tablet"]),
            "os": random.choice(["Windows", "macOS", "Linux", "Android", "iOS"]),
            "browser": random.choice(["Chrome", "Firefox", "Safari", "Edge"]),
            "resolution": f"{random.randint(800, 3840)}x{random.randint(600, 2160)}"
        }

    def generate_user_sessions(self, num_records: int = 1000) -> None:
        """Генерация данных для UserSessions"""
        sessions = []
        for _ in range(num_records):
            start_time = self.__fake.date_time_between(start_date="-1y", end_date="now")
            actions = []
            
            # Генерация действий
            for _ in range(random.randint(5, 20)):
                actions.append({
                    "action_type": random.choice(["click", "scroll", "login", "purchase", "search"]),
                    "timestamp": start_time + timedelta(seconds=random.randint(1, 300)),
                    "details": {
                        "page": self.__fake.uri_path(),
                        "duration": random.randint(1, 60)
                    }
                })
                
            sessions.append({
                "session_id": str(uuid4()),
                "user_id": random.choice(self.__user_ids),
                "start_time": start_time,
                "end_time": actions[-1]["timestamp"] if actions else None,
                "pages_visited": [self.__fake.uri_path() for _ in range(random.randint(3, 15))],
                "device": self._generate_device_info(),
                "actions": actions
            })
        
        try:
            self.__db.UserSessions.insert_many(sessions)
            logger.info(f"Inserted {num_records} UserSessions records")
        except PyMongoError as e:
            logger.error(f"Error inserting UserSessions: {e}")

    def generate_product_price_history(self) -> None:
        """Генерация данных для ProductPriceHistory"""
        products = []
        for product_id in self.__product_ids:
            price_changes = []
            current_price = random.uniform(10, 1000)
            
            for _ in range(random.randint(3, 10)):
                price_changes.append({
                    "price": (round(current_price + random.uniform(-20, 50), 2)),
                    "changed_at": self.__fake.date_time_between(start_date="-2y", end_date="now")
                })
                current_price = price_changes[-1]["price"]
                
            for price_dt in price_changes:
                price_dt["price"] = Decimal128(str(price_dt["price"]))

            current_price = Decimal128(str(current_price))

            products.append({
                "product_id": product_id,
                "price_changes": price_changes,
                "current_price": current_price,
                "currency": random.choice(["USD", "EUR", "RUB", "CNY"])
            })
        
        try:
            self.__db.ProductPriceHistory.insert_many(products)
            logger.info(f"Inserted {len(products)} ProductPriceHistory records")
        except PyMongoError as e:
            logger.error(f"Error inserting ProductPriceHistory: {e}")

    def generate_event_logs(self, num_records: int = 5000) -> None:
        """Генерация данных для EventLogs"""
        events = []
        for _ in range(num_records):
            event_type = random.choice(["user_action", "system", "transaction", "error"])
            events.append({
                "event_id": str(uuid4()),
                "timestamp": self.__fake.date_time_between(start_date="-1y", end_date="now"),
                "event_type": event_type,
                "details": {
                    "source": random.choice(["web", "mobile", "api", "backend"]),
                    "severity": random.choice(["low", "medium", "high", "critical"]) if event_type == "error" else None,
                    "metadata": {
                        "ip": self.__fake.ipv4(),
                        "user_agent": self.__fake.user_agent()
                    }
                }
            })
        
        try:
            self.__db.EventLogs.insert_many(events)
            logger.info(f"Inserted {num_records} EventLogs records")
        except PyMongoError as e:
            logger.error(f"Error inserting EventLogs: {e}")

    def generate_support_tickets(self, num_records: int = 300) -> None:
        """Генерация данных для SupportTickets"""
        tickets = []
        for _ in range(num_records):
            created_at = self.__fake.date_time_between(start_date="-6m", end_date="now")
            messages = []
            
            # Генерация сообщений
            for i in range(random.randint(1, 5)):
                messages.append({
                    "sender": "user" if i == 0 else random.choice(["user", "support"]),
                    "message": self.__fake.paragraph(nb_sentences=3),
                    "timestamp": created_at + timedelta(minutes=30*i)
                })
                
            tickets.append({
                "ticket_id": str(uuid4()),
                "user_id": random.choice(self.__user_ids),
                "status": random.choice(["open", "in_progress", "closed", "resolved"]),
                "issue_type": random.choice(["technical", "billing", "general", "refund"]),
                "messages": messages,
                "created_at": created_at,
                "updated_at": messages[-1]["timestamp"]
            })
        
        try:
            self.__db.SupportTickets.insert_many(tickets)
            logger.info(f"Inserted {num_records} SupportTickets records")
        except PyMongoError as e:
            logger.error(f"Error inserting SupportTickets: {e}")

    def generate_user_recommendations(self) -> None:
        """Генерация данных для UserRecommendations"""
        recommendations = []
        for user_id in self.__user_ids:
            recommendations.append({
                "user_id": user_id,
                "recommended_products": [{
                    "product_id": random.choice(self.__product_ids),
                    "score": round(random.uniform(0.5, 1.0), 4)
                } for _ in range(random.randint(5, 15))],
                "last_updated": self.__fake.date_time_between(start_date="-1m", end_date="now")
            })
        
        try:
            self.__db.UserRecommendations.insert_many(recommendations)
            logger.info(f"Inserted {len(recommendations)} UserRecommendations records")
        except PyMongoError as e:
            logger.error(f"Error inserting UserRecommendations: {e}")

    def generate_moderation_queue(self, num_records: int = 1000) -> None:
        """Генерация данных для ModerationQueue"""
        reviews = []
        for _ in range(num_records):
            reviews.append({
                "review_id": str(uuid4()),
                "user_id": random.choice(self.__user_ids),
                "product_id": random.choice(self.__product_ids),
                "review_text": self.__fake.paragraph(nb_sentences=2),
                "rating": random.randint(1, 5),
                "moderation_status": random.choice(["pending", "approved", "rejected"]),
                "flags": random.choices(["spam", "inappropriate", "fake"], k=random.randint(0, 2)),
                "submitted_at": self.__fake.date_time_between(start_date="-1m", end_date="now")
            })
        
        try:
            self.__db.ModerationQueue.insert_many(reviews)
            logger.info(f"Inserted {num_records} ModerationQueue records")
        except PyMongoError as e:
            logger.error(f"Error inserting ModerationQueue: {e}")

    def generate_search_queries(self, num_records: int = 2000) -> None:
        """Генерация данных для SearchQueries"""
        queries = []
        categories = ["electronics", "clothing", "books", "home", "toys"]
        
        for _ in range(num_records):
            has_filter = random.choice([True, False])
            
            queries.append({
                "query_id": str(uuid4()),
                "user_id": random.choice(self.__user_ids),
                "query_text": ' '.join(self.__fake.words(nb=random.randint(1, 3), unique=True)),
                "timestamp": self.__fake.date_time_between(start_date="-1y", end_date="now"),
                "filters": {
                    "price_range": {
                        "min": Decimal128(str(round(random.uniform(10, 500), 2))),
                        "max": Decimal128(str(round(random.uniform(500, 2000), 2)))
                    } if has_filter else None,
                    "category": random.choice(categories) if has_filter else None
                },
                "results_count": random.randint(0, 500)
            })
        
        try:
            self.__db.SearchQueries.insert_many(queries)
            logger.info(f"Inserted {num_records} SearchQueries records")
        except PyMongoError as e:
            logger.error(f"Error inserting SearchQueries: {e}")

    def generate_all_data(self):
        """Запуск генерации всех данных"""
        try:
            self.generate_user_sessions(self.__num_user_sessions)
            self.generate_product_price_history()
            self.generate_event_logs(self.__num_event_logs)
            self.generate_support_tickets(self.__num_event_logs)
            self.generate_user_recommendations()
            self.generate_moderation_queue(self.__num_moderation_queues)
            self.generate_search_queries(self.__num_search_queries)
            logger.info("All data generation completed successfully!")
        except Exception as e:
            logger.error(f"Critical error during data generation: {e}")
            raise

if __name__ == "__main__":
    mongo_generator = MongoDataGenerator()
    mongo_generator.generate_all_data()