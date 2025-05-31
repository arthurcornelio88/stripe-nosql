from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
print(client.list_database_names())  # Devrait inclure 'admin', 'local' et tout ce que tu as injecté
