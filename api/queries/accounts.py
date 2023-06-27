from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
client = MongoClient(DATABASE_URL)
db = client["pantry-pal-database"]


class DuplicateAccountError(ValueError):
    pass


class AccountIn(BaseModel):
    email: str
    username: str
    password: str


class AccountOut(BaseModel):
    id: str
    email: str
    username: str
    

class AccountOutWithPassword(AccountOut):
    hashed_password: str


class AccountQueries:
    @property
    def collection(self):
        return db["accounts"]
   
    def get(self, email: str) -> AccountOutWithPassword:
        account = self.collection.find_one({"email": email})
        if not account:
            return None
        account["id"] = str(ObjectId(account["_id"]))
        return AccountOutWithPassword(**account)

    def create(self, account_in: AccountIn, hashed_password: str) -> AccountOutWithPassword:
        account_data = account_in.dict()
        del account_data["password"]
        account_data["hashed_password"] = hashed_password
        try:
            self.collection.insert_one(account_data)
        except DuplicateKeyError:
            raise DuplicateAccountError()
        account_data["id"] = str(ObjectId(account_data["_id"]))
        return AccountOutWithPassword(**account_data)
