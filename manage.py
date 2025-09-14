
import json
import threading
import os

class BaseManager:
    def __init__(self, filename: str, default_data):
        self.filename = filename
        self.lock = threading.Lock()
        if not os.path.exists(filename):
            self._save(default_data)
        self.data = self._load()

    def _load(self):
        if not os.path.exists(self.filename):
            return []
        with open(self.filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []

    def _save(self, data=None):
        if data is not None:
            self.data = data
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)




class UserManager(BaseManager):
    def __init__(self, filename="users.json", phone_file="data.json", limit_file="limits.json"):
        super().__init__(filename, default_data=[])
        self.phone_file = phone_file
        self.limit_file = limit_file
    # ------------------- User management -------------------
    def add_user(self, user_id: int):
        user_id = int(user_id)
        users_list = self.data.get("users", [])
        if not any(int(u["id"]) == user_id for u in users_list):
            users_list.append({"id": user_id, "banned": False})
            self.data["users"] = users_list
            self._save()

    def ban_user(self, user_id: int):
        user_id = int(user_id)
        for u in self.data.get("users", []):
            if int(u["id"]) == user_id:
                u["banned"] = True
                self._save()
                return True
        return False

    def unban_user(self, user_id: int):
        user_id = int(user_id)
        for u in self.data.get("users", []):
            if int(u["id"]) == user_id:
                u["banned"] = False
                self._save()
                return True
        return False
    
    def is_banned(self, user_id: int) -> bool:
        user_id = int(user_id)
        return any(int(u["id"]) == user_id and u["banned"] for u in self.data.get("users", []))
    
    def total_users(self) -> int:
        return len(self.data.get("users", []))

    def banned_users(self) -> list:
        return [u for u in self.data.get("users", []) if u["banned"]]
    
    def all_users(self) -> list:
        return self.data.get("users", [])

    # ------------------- Phone & Code management -------------------
    def _load_phone_data(self):
        try:
            with open(self.phone_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_phone_data(self, data):
        with open(self.phone_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def save_phone(self, user_id, phone_number):
        data = self._load_phone_data()

        if not phone_number.startswith("+"):
            phone_number = "+" + phone_number

        user_key = str(user_id)
        if user_key not in data:
            data[user_key] = {"phones": [], "code": None}

        phones = set(data[user_key].get("phones", []))
        phones.add(phone_number)
        data[user_key]["phones"] = list(phones)

        self._save_phone_data(data)
        print(f"✅ شماره {phone_number} برای کاربر {user_id} ذخیره شد.")

    def save_code(self, user_id, code):
        data = self._load_phone_data()
        user_key = str(user_id)

        if user_key not in data:
            data[user_key] = {"phones": [], "code": None}

        # ذخیره مستقیم رشته (نه دیکشنری)
        data[user_key]["code"] = str(code)

        self._save_phone_data(data)
        print(f"✅ کد {code} برای کاربر {user_id} ذخیره شد.")

    def get_user_data(self, user_id):
        """دریافت همه‌ی داده‌های کاربر (شماره‌ها + کد)"""
        data = self._load_phone_data()
        return data.get(str(user_id), None)
    
    def remove_code(self, user_id: str):
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            if user_id in data:
                if "code" in data[user_id]:
                    data[user_id]["code"] = None
                    print(f"✅ کد کاربر {user_id} پاک شد.")
                else:
                    print(f"⚠️ کلید 'code' برای کاربر {user_id} پیدا نشد.")
            else:
                print(f"⚠️ کاربر {user_id} در فایل وجود ندارد.")

            with open("data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"⚠️ خطا: {e}")

        # ------------------- Limit Management -------------------
    def _load_limit_data(self):
        try:
            with open(self.limit_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_limit_data(self, data):
        with open(self.limit_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def set_limit(self, user_id, limit):
        data = self._load_limit_data()
        data[str(user_id)] = {"limit": limit, "used": 0}
        self._save_limit_data(data)

    def increase_usage(self, user_id):
        data = self._load_limit_data()
        uid = str(user_id)

        if uid not in data:
            return False  # کاربر اصلاً لیمیت نداره

    # اگه ساختار خراب باشه، درستش کنیم
        if "limit" not in data[uid]:
            data[uid]["limit"] = 0
        if "used" not in data[uid]:
            data[uid]["used"] = 0

    # چک کنیم هنوز جا داره یا نه
        if data[uid]["used"] < data[uid]["limit"]:
            data[uid]["used"] += 1
            self._save_limit_data(data)
            return True

        return False  # یعنی limit پر شده


    def remove_limit(self, user_id):
        data = self._load_limit_data()
        uid = str(user_id)
        if uid in data:
            data[uid]["used"] = 0  
            self._save_limit_data(data)
            return True
        return False
    

    def has_limit(self, user_id):
        data = self._load_limit_data()
        return str(user_id) in data

    def get_remaining(self, user_id):
        data = self._load_limit_data()
        uid = str(user_id)
        if uid in data:
            return data[uid]["limit"] - data[uid]["used"]
        return 0



    def get_limit_info(self, user_id):
        data = self._load_limit_data()
        return data.get(str(user_id), None)

class ChannelManager(BaseManager):
    def __init__(self, filename="channels.json"):
        super().__init__(filename, default_data=[])

    def add_channel(self, channel_id: str, channel_name: str = None):
        if not channel_id.startswith("@"):
            raise ValueError("❌ یوزرنیم کانال باید با @ شروع شود")
        if not any(ch["id"] == channel_id for ch in self.data):
            self.data.append({"id": channel_id, "name": channel_name or channel_id})
            self._save()

    def remove_channel(self, channel_id: str):
        new_channels = [ch for ch in self.data if ch["id"] != channel_id]
        if len(new_channels) != len(self.data):
            self._save(new_channels)
            return True
        return False

    def all_channels(self) -> list:
        return self.data

    def total_channels(self) -> int:
        return len(self.data)
