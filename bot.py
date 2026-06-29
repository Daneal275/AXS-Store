import sqlite3, json, asyncio
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.error import BadRequest
from datetime import datetime
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ================= CONFIG =================
TOKEN = "8920668290:AAHST_-UcDp_N5lUzLbPcnMqhOiuIEc7uXs"
ADMIN_ID = [7296029431, 7496515741]
CHANNEL = "@AXSGamingStore"
BALANCE_CHANNEL = "@axsgamesstore"
CHANNEL_ID = "@AXSGamingStore"
ADMIN_CHANNEL = "@accountwithadmin"
PRODUCT_ORDERS_CHANNEL = "@axsgameas"

# ================= DATABASE =================
conn = sqlite3.connect("store.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level INTEGER,
    likes INTEGER,
    prime INTEGER,
    evo INTEGER,
    dances INTEGER,
    link_type TEXT,
    recovery TEXT,
    price REAL,
    acc_type TEXT,
    images TEXT,
    channel_msg_ids TEXT,
    account_info TEXT
)
""")

try:
    cur.execute("ALTER TABLE accounts ADD COLUMN channel_msg_ids TEXT")
    conn.commit()
except:
    pass

try:
    cur.execute("ALTER TABLE accounts ADD COLUMN account_info TEXT")
    conn.commit()
except:
    pass

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    balance REAL DEFAULT 0,
    total_spent REAL DEFAULT 0,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

try:
    cur.execute("ALTER TABLE users ADD COLUMN total_spent REAL DEFAULT 0")
    conn.commit()
except:
    pass

try:
    cur.execute("ALTER TABLE users ADD COLUMN is_banned INTEGER DEFAULT 0")
    conn.commit()
except:
    pass

cur.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    acc_id INTEGER,
    user_id INTEGER,
    username TEXT,
    status TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    price REAL DEFAULT 0,
    paid_amount REAL DEFAULT 0,
    account_data TEXT,
    admin_msg_id INTEGER
)
""")

try:
    cur.execute("ALTER TABLE orders ADD COLUMN price REAL DEFAULT 0")
    conn.commit()
except:
    pass

try:
    cur.execute("ALTER TABLE orders ADD COLUMN paid_amount REAL DEFAULT 0")
    conn.commit()
except:
    pass

try:
    cur.execute("ALTER TABLE orders ADD COLUMN account_data TEXT")
    conn.commit()
except:
    pass

try:
    cur.execute("ALTER TABLE orders ADD COLUMN admin_msg_id INTEGER")
    conn.commit()
except:
    pass

cur.execute("""
CREATE TABLE IF NOT EXISTS balance_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    amount REAL,
    payment_method TEXT,
    transaction_number TEXT,
    status TEXT DEFAULT 'pending',
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    channel_msg_id INTEGER,
    processed_date TIMESTAMP
)
""")

try:
    cur.execute("ALTER TABLE balance_requests ADD COLUMN channel_msg_id INTEGER")
    conn.commit()
except:
    pass

try:
    cur.execute("ALTER TABLE balance_requests ADD COLUMN transaction_number TEXT")
    conn.commit()
except:
    pass

try:
    cur.execute("ALTER TABLE balance_requests ADD COLUMN processed_date TIMESTAMP")
    conn.commit()
except:
    pass

cur.execute("""
CREATE TABLE IF NOT EXISTS payment_methods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

try:
    cur.execute("ALTER TABLE payment_methods ADD COLUMN description TEXT")
    conn.commit()
except:
    pass

try:
    cur.execute("ALTER TABLE payment_methods ADD COLUMN currency TEXT DEFAULT 'USD'")
    conn.commit()
except:
    pass

try:
    cur.execute("ALTER TABLE payment_methods ADD COLUMN exchange_rate REAL DEFAULT 1")
    conn.commit()
except:
    pass

cur.execute("""
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")

cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('support_text', '📞 للتواصل: @AXS_Admin')")

cur.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER DEFAULT NULL,
    level INTEGER DEFAULT 1,
    price REAL DEFAULT 0,
    is_product INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE CASCADE
)
""")

try:
    cur.execute("ALTER TABLE categories ADD COLUMN price REAL DEFAULT 0")
    conn.commit()
except:
    pass

try:
    cur.execute("ALTER TABLE categories ADD COLUMN is_product INTEGER DEFAULT 0")
    conn.commit()
except:
    pass

try:
    cur.execute("ALTER TABLE categories ADD COLUMN is_active INTEGER DEFAULT 1")
    conn.commit()
except:
    pass

cur.execute("""
CREATE TABLE IF NOT EXISTS product_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    product_id INTEGER,
    product_name TEXT,
    category_name TEXT,
    price REAL,
    player_id TEXT,
    status TEXT DEFAULT 'pending',
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    channel_msg_id INTEGER,
    processed_date TIMESTAMP,
    admin_response TEXT
)
""")

try:
    cur.execute("ALTER TABLE product_orders ADD COLUMN channel_msg_id INTEGER")
    conn.commit()
except:
    pass

try:
    cur.execute("ALTER TABLE product_orders ADD COLUMN processed_date TIMESTAMP")
    conn.commit()
except:
    pass

try:
    cur.execute("ALTER TABLE product_orders ADD COLUMN admin_response TEXT")
    conn.commit()
except:
    pass

conn.commit()

cur.execute("SELECT COUNT(*) FROM payment_methods")
if cur.fetchone()[0] == 0:
    cur.execute("""
    INSERT INTO payment_methods (name, description, currency, exchange_rate) VALUES 
    ('سيرياتيل كاش', 'الرجاء التحويل على أحد الأرقام التالية:\n📱 0991234567\n📱 0987654321', 'USD', 1),
    ('شام كاش', 'حول على الرابط التالي:\n🔗 https://shamcash.com/pay/12345', 'USD', 1),
    ('طرق أخرى', 'للتواصل مع الدعم الفني لحجز موعد دفع', 'USD', 1)
    """)
    conn.commit()

cur.execute("SELECT COUNT(*) FROM categories")
if cur.fetchone()[0] == 0:
    cur.execute("INSERT INTO categories (name, parent_id, level) VALUES ('📱 تطبيقات', NULL, 1)")
    cur.execute("INSERT INTO categories (name, parent_id, level) VALUES ('🎮 ألعاب', NULL, 1)")
    cur.execute("INSERT INTO categories (name, parent_id, level) VALUES ('💳 بطاقات', NULL, 1)")
    conn.commit()

admin_data = {}
user_data = {}

# ================= وظائف مساعدة =================
def get_support_text():
    result = cur.execute("SELECT value FROM settings WHERE key = 'support_text'").fetchone()
    if result:
        return result[0]
    return "📞 للتواصل: @AXS_Admin"

async def check_subscription(user_id, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status not in ['left', 'kicked']
    except:
        return False

def calculate_time_difference(request_date_str):
    try:
        processed_time = datetime.now()
        request_time = datetime.strptime(request_date_str, '%Y-%m-%d %H:%M:%S')
        time_diff = processed_time - request_time
        total_seconds = int(time_diff.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours} ساعة و {minutes} دقيقة و {seconds} ثانية"
        elif minutes > 0:
            return f"{minutes} دقيقة و {seconds} ثانية"
        else:
            return f"{seconds} ثانية"
    except:
        return "غير معروف"

async def delete_channel_messages(context, msg_ids_str):
    if not msg_ids_str or msg_ids_str.strip() == "":
        return False
    try:
        msg_ids = [int(x.strip()) for x in msg_ids_str.split(",") if x.strip()]
        if not msg_ids:
            return False
        deleted_count = 0
        for msg_id in msg_ids:
            try:
                await context.bot.delete_message(CHANNEL, msg_id)
                deleted_count += 1
            except:
                pass
        return deleted_count > 0
    except:
        return False

async def restore_account_to_channel(context, account_data, new_acc_id):
    try:
        images_list = account_data["images"].split(",")
        caption = (
            f"🎮 حساب #{new_acc_id}\n"
            f"{'─' * 30}\n"
            f"📊 • اللفل: {account_data['level']}\n"
            f"❤️ • اللايكات: {account_data['likes']}\n"
            f"👑 • البرايم: {account_data['prime']}\n"
            f"⚔️ • الإيفو: {account_data['evo']}\n"
            f"💃 • الرقصات: {account_data['dances']}\n"
            f"🔗 • الربط: {account_data['link_type']}\n"
            f"♻️ • استعادة: {account_data['recovery']}\n"
            f"📦 • النوع: {account_data['acc_type']}\n"
            f"💰 • السعر: {account_data['price']}$"
        )
        media = []
        for i, img in enumerate(images_list):
            if i == 0:
                media.append(InputMediaPhoto(media=img, caption=caption))
            else:
                media.append(InputMediaPhoto(media=img))
        sent_messages = await context.bot.send_media_group(CHANNEL, media)
        new_msg_ids = ",".join([str(msg.message_id) for msg in sent_messages])
        cur.execute("UPDATE accounts SET channel_msg_ids = ? WHERE id = ?", (new_msg_ids, new_acc_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ فشل إعادة الحساب للقناة: {e}")
        return False

async def update_channel_message(context, acc_id, account_data):
    try:
        cur.execute("SELECT channel_msg_ids FROM accounts WHERE id = ?", (acc_id,))
        row = cur.fetchone()
        if not row or not row[0]:
            return False
        old_msg_ids = [int(x.strip()) for x in row[0].split(",") if x.strip()]
        images_list = account_data["images"].split(",")
        caption = (
            f"🎮 حساب #{acc_id}\n{'─' * 30}\n"
            f"📊 • اللفل: {account_data['level']}\n"
            f"❤️ • اللايكات: {account_data['likes']}\n"
            f"👑 • البرايم: {account_data['prime']}\n"
            f"⚔️ • الإيفو: {account_data['evo']}\n"
            f"💃 • الرقصات: {account_data['dances']}\n"
            f"🔗 • الربط: {account_data['link_type']}\n"
            f"♻️ • استعادة: {account_data['recovery']}\n"
            f"📦 • النوع: {account_data['acc_type']}\n"
            f"💰 • السعر: {account_data['price']}$\n\n"
            f"✏️ تم التعديل: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        media = []
        for i, img in enumerate(images_list):
            if i == 0:
                media.append(InputMediaPhoto(media=img, caption=caption))
            else:
                media.append(InputMediaPhoto(media=img))
        sent_messages = await context.bot.send_media_group(CHANNEL, media)
        new_msg_ids = ",".join([str(msg.message_id) for msg in sent_messages])
        cur.execute("UPDATE accounts SET channel_msg_ids = ? WHERE id = ?", (new_msg_ids, acc_id))
        conn.commit()
        for msg_id in old_msg_ids:
            try:
                await context.bot.delete_message(CHANNEL, msg_id)
            except:
                pass
        return True
    except Exception as e:
        print(f"❌ فشل تعديل رسالة القناة: {e}")
        return False

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        
        if user.id not in ADMIN_ID:
            cur.execute("SELECT is_banned FROM users WHERE user_id = ?", (user.id,))
            banned = cur.fetchone()
            if banned and banned[0] == 1:
                await update.message.reply_text("⛔ أنت محظور من استخدام البوت")
                return
        
        is_subscribed = await check_subscription(user.id, context)
        
        if not is_subscribed:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 قناتنا الرسمية", url=f"https://t.me/{CHANNEL.replace('@', '')}")],
                [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")]
            ])
            await update.message.reply_text(
                "⚠️ يجب عليك الاشتراك في القناة أولاً لاستخدام البوت\n\n"
                "بعد الاشتراك، اضغط على زر التحقق ✅",
                reply_markup=keyboard
            )
            return
        
        cur.execute("INSERT OR IGNORE INTO users (user_id, username, balance, total_spent) VALUES (?, ?, 0, 0)", 
                    (user.id, user.username))
        conn.commit()
        
        if user.id in admin_data: del admin_data[user.id]
        if user.id in user_data: del user_data[user.id]
        if 'delete_mode' in context.user_data: del context.user_data['delete_mode']
        
        cur.execute("SELECT acc_type, COUNT(*) FROM accounts GROUP BY acc_type")
        counts = {row[0]: row[1] for row in cur.fetchall()}
        
        keyboard = [
            [f"🎮 عرض الحسابات ({sum(counts.values())})"],
            ["🛍 المنتجات"],
            ["💰 إضافة رصيد", "👤 حسابي"],
            ["📞 الدعم الفني"]
        ]

        if user.id in ADMIN_ID:
            keyboard.append(["📊 لوحة الأدمن"])

        await update.message.reply_text(
            "🎮 أهلاً بك في AXS STORE\nاختر الخدمة التي تريدها:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
    except Exception as e:
        print(f"Error in start: {e}")

# ================= CHECK SUBSCRIPTION CALLBACK =================
async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if user_id not in ADMIN_ID:
        cur.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
        banned = cur.fetchone()
        if banned and banned[0] == 1:
            await query.answer("⛔ أنت محظور من استخدام البوت", show_alert=True)
            return
    
    is_subscribed = await check_subscription(user_id, context)
    
    if is_subscribed:
        await query.message.delete()
        await start(update, context)
    else:
        await query.answer("❌ لم تشترك بعد، اشترك ثم حاول مرة أخرى", show_alert=True)

# ================= HANDLE DELIVERY INFO =================
async def handle_delivery_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        if not user:
            return
        user_id = user.id
        if user_id not in admin_data:
            return
        d = admin_data[user_id]
        if d.get("step") != "deliver_info":
            return
        
        delivery_info = update.message.text
        order_id = d["order_id"]
        buyer_id = d["buyer_id"]
        acc_id = d["acc_id"]
        price = d["price"]
        admin_msg_id = d["admin_msg_id"]
        
        cur.execute("UPDATE orders SET status = 'completed' WHERE id = ?", (order_id,))
        conn.commit()
        
        try:
            await context.bot.send_message(
                chat_id=buyer_id,
                text=(
                    f"🎮 معلومات حسابك #{acc_id}\n"
                    f"{'─' * 30}\n\n"
                    f"{delivery_info}\n\n"
                    f"{'─' * 30}\n"
                    f"💰 السعر: ${price:.2f}\n\n"
                    f"شكراً لثقتك بنا 💚\n"
                    f"لأي استفسار: @AXS_Admin"
                )
            )
            await update.message.reply_text("✅ تم إرسال المعلومات للمشتري بنجاح")
        except Exception as e:
            print(f"❌ فشل إرسال الرسالة للمشتري: {e}")
            await update.message.reply_text(
                f"❌ فشل إرسال المعلومات للمشتري!\n\n"
                f"السبب: {str(e)}\n\n"
                f"👤 معرف المشتري: `{buyer_id}`"
            )
            del admin_data[user_id]
            return
        
        if admin_msg_id:
            try:
                await context.bot.delete_message(chat_id=ADMIN_CHANNEL, message_id=admin_msg_id)
            except:
                pass
            try:
                await context.bot.send_message(
                    chat_id=ADMIN_CHANNEL,
                    text=(
                        f"🛒 عملية بيع مكتملة ✅\n{'─' * 30}\n"
                        f"🎮 رقم الحساب: #{acc_id}\n"
                        f"👤 المشتري: `{buyer_id}`\n"
                        f"💰 السعر: ${price:.2f}\n\n"
                        f"📝 معلومات الحساب:\n{delivery_info}\n\n"
                        f"✅ تم التسليم للمشتري\n"
                        f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    )
                )
            except:
                pass
        
        del admin_data[user_id]
        return
        
    except Exception as e:
        print(f"Error in handle_delivery_info: {e}")

# ================= CATEGORIES CALLBACK =================
async def categories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        data = query.data
        
        if data == "show_categories":
            categories = cur.execute("SELECT id, name FROM categories WHERE parent_id IS NULL ORDER BY id").fetchall()
            if not categories:
                await query.message.edit_text("❌ لا توجد فئات حالياً")
                return
            
            msg = (
                f"🛍 • المنتجات المتاحة\n"
                f"━━━━━━━━━━━━━━━━━━━\n\n"
                f"اختر الفئة اللي بدك تتصفحها:\n"
            )
            keyboard = []
            row = []
            for c in categories:
                row.append(InlineKeyboardButton(f"{c[1]}", callback_data=f"cat_{c[0]}"))
                if len(row) == 2:
                    keyboard.append(row)
                    row = []
            if row:
                keyboard.append(row)
            
            await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
            return
        
        if data.startswith("cat_"):
            cat_id = int(data.split("_")[1])
            
            # التحقق من حالة الفئة
            cat_status = cur.execute("SELECT is_active FROM categories WHERE id = ?", (cat_id,)).fetchone()
            if cat_status and cat_status[0] == 0:
                # الرجوع للقائمة الرئيسية مع رسالة
                categories = cur.execute("SELECT id, name FROM categories WHERE parent_id IS NULL ORDER BY id").fetchall()
                msg = (
                    f"⚠️ • هذه الفئة غير متوفرة حالياً\n\n"
                    f"🛍 • المنتجات المتاحة\n"
                    f"━━━━━━━━━━━━━━━━━━━\n\n"
                    f"اختر الفئة اللي بدك تتصفحها:\n"
                )
                keyboard = []
                row = []
                for c in categories:
                    row.append(InlineKeyboardButton(f"{c[1]}", callback_data=f"cat_{c[0]}"))
                    if len(row) == 2:
                        keyboard.append(row)
                        row = []
                if row:
                    keyboard.append(row)
                
                await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
                return
            
            category = cur.execute("SELECT name, level, parent_id, is_product, price FROM categories WHERE id = ?", (cat_id,)).fetchone()
            if not category:
                await query.message.edit_text("❌ الفئة غير موجودة")
                return
            
            cat_name, level, parent_id, is_product, price = category
            
            if is_product == 1:
                parent_name = cur.execute("SELECT name FROM categories WHERE id = ?", (parent_id,)).fetchone()
                parent_name = parent_name[0] if parent_name else ""
                
                msg = (
                    f"🛒 • تفاصيل المنتج\n"
                    f"━━━━━━━━━━━━━━━━━━━\n\n"
                    f"🎮 اللعبة : {parent_name}\n"
                    f"📦 المنتج : {cat_name}\n"
                    f"💰 السعر : ${price:.2f}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━\n\n"
                    f"للشراء اضغط على الزر أدناه ✨"
                )
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🛒 شراء المنتج", callback_data=f"buy_product_{cat_id}")],
                    [InlineKeyboardButton("🔙 رجوع", callback_data=f"cat_{parent_id}")]
                ])
                await query.message.edit_text(msg, reply_markup=keyboard)
                return
            
            subcategories = cur.execute("SELECT id, name, level, is_product, price FROM categories WHERE parent_id = ? ORDER BY is_product, id", (cat_id,)).fetchall()
            
            if not subcategories:
                msg = (
                    f"📂 • {cat_name}\n"
                    f"━━━━━━━━━━━━━━━━━━━\n\n"
                    f"لا توجد خدمات حالياً 🌙\n\n"
                    f"للشراء تواصل مع الدعم الفني:\n"
                    f"💬 @AXS_Admin"
                )
                if parent_id:
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 رجوع", callback_data=f"cat_{parent_id}")],
                        [InlineKeyboardButton("🔙 للفئات الرئيسية", callback_data="show_categories")]
                    ])
                else:
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 للفئات الرئيسية", callback_data="show_categories")]
                    ])
                await query.message.edit_text(msg, reply_markup=keyboard)
                return
            
            msg = (
                f"📂 • {cat_name}\n"
                f"━━━━━━━━━━━━━━━━━━━\n\n"
                f"اختر الخدمة اللي بدك إياها:\n"
            )
            keyboard = []
            row = []
            for sc in subcategories:
                label = f"{sc[1]}"
                if sc[3] == 1:
                    label = f"{sc[1]} - ${sc[4]:.2f}"
                row.append(InlineKeyboardButton(label, callback_data=f"cat_{sc[0]}"))
                if len(row) == 2:
                    keyboard.append(row)
                    row = []
            if row:
                keyboard.append(row)
            if parent_id:
                keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data=f"cat_{parent_id}")])
            keyboard.append([InlineKeyboardButton("🔙 للفئات الرئيسية", callback_data="show_categories")])
            await query.message.edit_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
            return
        
        # ===== شراء منتج =====
        if data.startswith("buy_product_"):
            product_id = int(data.split("_")[2])
            product = cur.execute("""
                SELECT c.name, c.price, p.name 
                FROM categories c 
                JOIN categories p ON c.parent_id = p.id 
                WHERE c.id = ? AND c.is_product = 1
            """, (product_id,)).fetchone()
            
            if not product:
                await query.answer("❌ المنتج غير موجود", show_alert=True)
                return
            
            product_name, price, category_name = product
            user_id = query.from_user.id
            user_data[user_id] = {
                "step": "product_order",
                "product_id": product_id,
                "product_name": product_name,
                "category_name": category_name,
                "price": price
            }
            
            msg = (
                f"🛒 • طلب شراء منتج\n"
                f"━━━━━━━━━━━━━━━━━━━\n\n"
                f"🎮 اللعبة : {category_name}\n"
                f"📦 المنتج : {product_name}\n"
                f"💰 السعر : ${price:.2f}\n\n"
                f"━━━━━━━━━━━━━━━━━━━\n\n"
                f"📩 الرجاء إدخال الإيدي (أرقام فقط):"
            )
            await query.message.edit_text(msg)
            return
        
        # ===== تأكيد طلب المنتج =====
        if data.startswith("confirm_product_"):
            parts = data.split("_")
            product_id = int(parts[2])
            player_id = parts[3]
            
            user = query.from_user
            user_id = user.id
            
            if user_id not in user_data or user_data[user_id].get("step") != "confirm_product":
                await query.answer("❌ انتهت الجلسة", show_alert=True)
                return
            
            d = user_data[user_id]
            
            cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            user_balance = cur.fetchone()
            
            if not user_balance or user_balance[0] < d["price"]:
                shortage = d["price"] - (user_balance[0] if user_balance else 0)
                await query.answer(
                    f"❌ الرصيد غير كافي!\n\n"
                    f"💰 السعر: ${d['price']:.2f}\n"
                    f"💳 رصيدك: ${user_balance[0]:.2f}\n"
                    f"📉 الناقص: ${shortage:.2f}\n\n"
                    f"الرجاء تعبئة حسابك",
                    show_alert=True
                )
                return
            
            new_balance = user_balance[0] - d["price"]
            cur.execute("UPDATE users SET balance = ?, total_spent = total_spent + ? WHERE user_id = ?", 
                      (new_balance, d["price"], user_id))
            
            cur.execute("""
                INSERT INTO product_orders (user_id, username, product_id, product_name, category_name, price, player_id, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
            """, (user_id, user.username, product_id, d["product_name"], d["category_name"], d["price"], player_id))
            conn.commit()
            order_id = cur.lastrowid
            
            caption = (
                f"📋 طلب جديد\n{'─' * 30}\n"
                f"👤 المستخدم: @{user.username or 'بدون يوزر'}\n"
                f"🆔 معرف المستخدم: `{user_id}`\n"
                f"🎮 اسم اللعبة: {d['category_name']}\n"
                f"📦 المنتج: {d['product_name']}\n"
                f"💰 السعر: ${d['price']:.2f}\n"
                f"🎯 إيدي اللاعب: `{player_id}`\n"
                f"🆔 رقم الطلب: #{order_id}\n"
                f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                f"الحالة: ⏳ قيد الانتظار"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ قبول", callback_data=f"approve_product_{order_id}"),
                 InlineKeyboardButton("❌ رفض", callback_data=f"reject_product_{order_id}")]
            ])
            
            sent_msg = await context.bot.send_message(PRODUCT_ORDERS_CHANNEL, caption, reply_markup=keyboard)
            cur.execute("UPDATE product_orders SET channel_msg_id = ? WHERE id = ?", (sent_msg.message_id, order_id))
            conn.commit()
            
            await query.message.edit_text(
                f"✅ تم إرسال طلبك بنجاح!\n\n"
                f"📋 طلبك قيد المعالجة ⏳\n{'─' * 30}\n"
                f"🎮 اسم اللعبة: {d['category_name']}\n"
                f"📦 المنتج: {d['product_name']}\n"
                f"💰 السعر: ${d['price']:.2f}\n"
                f"🎯 الإيدي: `{player_id}`\n"
                f"🆔 رقم الطلب: #{order_id}\n\n"
                f"سيتم مراجعة طلبك من قبل الإدارة 🌹"
            )
            del user_data[user_id]
            return
        
        # ===== إلغاء طلب المنتج =====
        if data.startswith("cancel_product_"):
            user_id = query.from_user.id
            if user_id in user_data:
                del user_data[user_id]
            await query.message.edit_text("❌ تم إلغاء الطلب")
            return
        
        # ===== قبول طلب (أدمن) =====
        if data.startswith("approve_product_"):
            if query.from_user.id not in ADMIN_ID:
                await query.answer("❌ غير مصرح", show_alert=True)
                return
            
            order_id = int(data.split("_")[2])
            order = cur.execute("SELECT * FROM product_orders WHERE id = ? AND status = 'pending'", (order_id,)).fetchone()
            if not order:
                await query.answer("❌ الطلب غير موجود أو تمت معالجته", show_alert=True)
                return
            
            admin_data[query.from_user.id] = {
                "step": "deliver_product",
                "order_id": order_id,
                "buyer_id": order[1],
                "product_name": order[4],
                "category_name": order[5],
                "price": order[6],
                "player_id": order[7],
                "channel_msg_id": order[10]
            }
            
            await context.bot.send_message(
                chat_id=query.from_user.id,
                text=(
                    f"📝 أدخل الرسالة التي سترسلها للزبون:\n\n"
                    f"🎮 اللعبة: {order[5]}\n"
                    f"📦 المنتج: {order[4]}\n"
                    f"🎯 الإيدي: {order[7]}\n\n"
                    f"اكتب رسالة التسليم:"
                )
            )
            return
        
        # ===== رفض طلب (أدمن) =====
        if data.startswith("reject_product_"):
            if query.from_user.id not in ADMIN_ID:
                await query.answer("❌ غير مصرح", show_alert=True)
                return
            
            order_id = int(data.split("_")[2])
            order = cur.execute("SELECT * FROM product_orders WHERE id = ? AND status = 'pending'", (order_id,)).fetchone()
            if not order:
                await query.answer("❌ الطلب غير موجود أو تمت معالجته", show_alert=True)
                return
            
            cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (order[6], order[1]))
            processed_time = datetime.now()
            cur.execute("UPDATE product_orders SET status = 'rejected', processed_date = ? WHERE id = ?", 
                      (processed_time, order_id))
            conn.commit()
            
            time_str = calculate_time_difference(order[9])
            
            if order[10]:
                try:
                    caption = (
                        f"📋 طلب جديد\n{'─' * 30}\n"
                        f"👤 المستخدم: @{order[2] or 'بدون يوزر'}\n"
                        f"🆔 معرف المستخدم: `{order[1]}`\n"
                        f"🎮 اسم اللعبة: {order[5]}\n"
                        f"📦 المنتج: {order[4]}\n"
                        f"💰 السعر: ${order[6]:.2f}\n"
                        f"🎯 إيدي اللاعب: `{order[7]}`\n"
                        f"🆔 رقم الطلب: #{order_id}\n"
                        f"📅 التاريخ: {order[9][:16]}\n\n"
                        f"❌ تم الرفض\n"
                        f"⏱ وقت المعالجة: {time_str}"
                    )
                    await context.bot.edit_message_text(
                        chat_id=PRODUCT_ORDERS_CHANNEL,
                        message_id=order[10],
                        text=caption
                    )
                except:
                    pass
            
            try:
                await context.bot.send_message(
                    order[1],
                    f"❌ تم رفض طلبك\n{'─' * 30}\n"
                    f"🎮 اللعبة: {order[5]}\n"
                    f"📦 المنتج: {order[4]}\n"
                    f"💰 تم استرداد: ${order[6]:.2f}\n"
                    f"⏱ وقت المعالجة: {time_str}\n\n"
                    f"نعتذر عن عدم تلبية طلبك\n"
                    f"الرجاء التواصل مع الدعم: @AXS_Admin"
                )
            except:
                pass
            
            await query.answer("✅ تم رفض الطلب", show_alert=True)
            return
        
    except Exception as e:
        print(f"Error in categories_callback: {e}")

# ================= UNIVERSAL HANDLER =================
async def universal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        if not user:
            return
        
        user_id = user.id
        text = update.message.text.strip()
        
        if user_id not in ADMIN_ID:
            cur.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
            banned = cur.fetchone()
            if banned and banned[0] == 1:
                await update.message.reply_text("⛔ أنت محظور من استخدام البوت")
                return
        
        if user_id in ADMIN_ID and user_id in admin_data:
            if admin_data[user_id].get("step") == "deliver_info":
                await handle_delivery_info(update, context)
                return
            if admin_data[user_id].get("step") == "deliver_product":
                d = admin_data[user_id]
                delivery_msg = text
                order_id = d["order_id"]
                buyer_id = d["buyer_id"]
                channel_msg_id = d["channel_msg_id"]
                
                processed_time = datetime.now()
                cur.execute("UPDATE product_orders SET status = 'completed', admin_response = ?, processed_date = ? WHERE id = ?", 
                          (delivery_msg, processed_time, order_id))
                conn.commit()
                
                order = cur.execute("SELECT * FROM product_orders WHERE id = ?", (order_id,)).fetchone()
                time_str = calculate_time_difference(order[9])
                
                if channel_msg_id:
                    try:
                        caption = (
                            f"📋 طلب جديد\n{'─' * 30}\n"
                            f"👤 المستخدم: @{order[2] or 'بدون يوزر'}\n"
                            f"🆔 معرف المستخدم: `{order[1]}`\n"
                            f"🎮 اسم اللعبة: {order[5]}\n"
                            f"📦 المنتج: {order[4]}\n"
                            f"💰 السعر: ${order[6]:.2f}\n"
                            f"🎯 إيدي اللاعب: `{order[7]}`\n"
                            f"🆔 رقم الطلب: #{order_id}\n"
                            f"📅 التاريخ: {order[9][:16]}\n\n"
                            f"✅ تم القبول\n"
                            f"📝 رسالة الأدمن: {delivery_msg}\n"
                            f"⏱ وقت المعالجة: {time_str}"
                        )
                        await context.bot.edit_message_text(
                            chat_id=PRODUCT_ORDERS_CHANNEL,
                            message_id=channel_msg_id,
                            text=caption
                        )
                    except:
                        pass
                
                try:
                    await context.bot.send_message(
                        buyer_id,
                        f"✅ تم قبول طلبك!\n{'─' * 30}\n"
                        f"🎮 اللعبة: {d['category_name']}\n"
                        f"📦 المنتج: {d['product_name']}\n"
                        f"💰 السعر: ${d['price']:.2f}\n"
                        f"🎯 الإيدي: {d['player_id']}\n\n"
                        f"📝 رسالة الأدمن:\n{delivery_msg}\n\n"
                        f"شكراً لثقتك بنا 💚"
                    )
                except:
                    pass
                
                await update.message.reply_text("✅ تم إرسال الرسالة للزبون")
                del admin_data[user_id]
                return
        
        is_subscribed = await check_subscription(user_id, context)
        if not is_subscribed:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 قناتنا الرسمية", url=f"https://t.me/{CHANNEL.replace('@', '')}")],
                [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")]
            ])
            await update.message.reply_text(
                "⚠️ يجب عليك الاشتراك في القناة أولاً لاستخدام البوت\n\n"
                "بعد الاشتراك، اضغط على زر التحقق ✅",
                reply_markup=keyboard
            )
            return
        
        print(f"📩 [{user_id}] @{user.username}: {text}")

        # ============ خطوات المستخدم - طلب منتج ============
        if user_id in user_data and user_data[user_id].get("step") == "product_order":
            if not text.isdigit():
                await update.message.reply_text("⚠️ الإيدي يجب أن يكون أرقام فقط! الرجاء إدخال الإيدي:")
                return
            
            player_id = text
            d = user_data[user_id]
            d["player_id"] = player_id
            d["step"] = "confirm_product"
            
            cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            current_balance = cur.fetchone()[0]
            after_balance = current_balance - d['price']
            
            msg = (
                f"⚠️ • تأكيد الطلب\n"
                f"━━━━━━━━━━━━━━━━━━━\n\n"
                f"🎮 اللعبة : {d['category_name']}\n"
                f"📦 المنتج : {d['product_name']}\n"
                f"💰 السعر : ${d['price']:.2f}\n"
                f"🎯 الإيدي : `{player_id}`\n\n"
                f"💳 رصيدك الحالي : ${current_balance:.2f}\n"
                f"💸 رصيدك بعد الشراء : ${after_balance:.2f}\n\n"
                f"━━━━━━━━━━━━━━━━━━━"
            )
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ تأكيد", callback_data=f"confirm_product_{d['product_id']}_{player_id}"),
                 InlineKeyboardButton("❌ رفض", callback_data="cancel_product_0")]
            ])
            
            await update.message.reply_text(msg, reply_markup=keyboard)
            return
        
        # ============ خطوات الأدمن ============
        if user_id in ADMIN_ID:
            
            if context.user_data.get('delete_mode'):
                try:
                    acc_id = int(text)
                    cur.execute("SELECT channel_msg_ids FROM accounts WHERE id = ?", (acc_id,))
                    row = cur.fetchone()
                    if row and row[0]:
                        await delete_channel_messages(context, row[0])
                    cur.execute("DELETE FROM accounts WHERE id = ?", (acc_id,))
                    conn.commit()
                    await update.message.reply_text(f"✅ تم حذف الحساب #{acc_id}")
                except ValueError:
                    await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                context.user_data['delete_mode'] = False
                return
            
            if user_id in admin_data:
                d = admin_data[user_id]
                
                if d.get("step") == "broadcast":
                    if text == "إلغاء":
                        await update.message.reply_text("❌ تم إلغاء الإذاعة")
                        del admin_data[user_id]
                        return
                    
                    users = cur.execute("SELECT user_id FROM users WHERE is_banned = 0").fetchall()
                    success = 0
                    fail = 0
                    status_msg = await update.message.reply_text("📤 جاري إرسال الرسالة...")
                    for u in users:
                        try:
                            await context.bot.send_message(u[0], f"📢 رسالة من الإدارة\n\n{text}")
                            success += 1
                        except:
                            fail += 1
                        await asyncio.sleep(0.05)
                    await status_msg.edit_text(
                        f"✅ تم إرسال الإذاعة\n\n"
                        f"📊 الإحصائيات:\n"
                        f"✅ نجح: {success}\n"
                        f"❌ فشل: {fail}\n"
                        f"👥 المجموع: {len(users)}"
                    )
                    del admin_data[user_id]
                    return
                
                if d.get("step") == "modify_balance_user":
                    if text == "إلغاء":
                        await update.message.reply_text("❌ تم الإلغاء")
                        del admin_data[user_id]
                        return
                    
                    username = text.replace("@", "").strip()
                    if username.isdigit():
                        user_found = cur.execute("SELECT user_id, username, balance FROM users WHERE user_id = ?", (int(username),)).fetchone()
                    else:
                        user_found = cur.execute("SELECT user_id, username, balance FROM users WHERE username = ?", (username,)).fetchone()
                    
                    if not user_found:
                        await update.message.reply_text("❌ المستخدم غير موجود في البوت")
                        del admin_data[user_id]
                        return
                    
                    d["target_user_id"] = user_found[0]
                    d["target_username"] = user_found[1]
                    d["current_balance"] = user_found[2]
                    d["step"] = "modify_balance_amount"
                    
                    await update.message.reply_text(
                        f"👤 المستخدم: @{user_found[1] or user_found[0]}\n"
                        f"💰 الرصيد الحالي: ${user_found[2]:.2f}\n\n"
                        "أرسل المبلغ:\n"
                        "• 50 = إضافة 50$\n"
                        "• -30 = خصم 30$\n\n"
                        "للإلغاء أرسل: إلغاء"
                    )
                    return
                
                if d.get("step") == "modify_balance_amount":
                    if text == "إلغاء":
                        await update.message.reply_text("❌ تم الإلغاء")
                        del admin_data[user_id]
                        return
                    
                    try:
                        amount = float(text)
                        new_balance = d["current_balance"] + amount
                        cur.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, d["target_user_id"]))
                        conn.commit()
                        
                        try:
                            if amount > 0:
                                msg = f"💰 تم إضافة رصيد\n\nالمبلغ: +${amount:.2f}\nرصيدك الحالي: ${new_balance:.2f}"
                            else:
                                msg = f"💰 تم خصم رصيد\n\nالمبلغ: -${abs(amount):.2f}\nرصيدك الحالي: ${new_balance:.2f}"
                            await context.bot.send_message(d["target_user_id"], msg)
                        except:
                            pass
                        
                        await update.message.reply_text(
                            f"✅ تم تعديل الرصيد بنجاح\n\n"
                            f"👤 المستخدم: @{d['target_username'] or d['target_user_id']}\n"
                            f"💰 السابق: ${d['current_balance']:.2f}\n"
                            f"{'🟢 إضافة' if amount > 0 else '🔴 خصم'}: ${abs(amount):.2f}\n"
                            f"💰 الجديد: ${new_balance:.2f}"
                        )
                    except ValueError:
                        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                        return
                    del admin_data[user_id]
                    return
                
                # ===== حظر مستخدم =====
                if d.get("step") == "ban_user":
                    if text == "إلغاء":
                        await update.message.reply_text("❌ تم الإلغاء")
                        del admin_data[user_id]
                        return
                    try:
                        target_id = int(text)
                        user_found = cur.execute("SELECT user_id, username, is_banned FROM users WHERE user_id = ?", (target_id,)).fetchone()
                        if not user_found:
                            await update.message.reply_text("❌ المستخدم غير موجود في البوت")
                            del admin_data[user_id]
                            return
                        if user_found[2] == 1:
                            await update.message.reply_text("⚠️ هذا المستخدم محظور بالفعل")
                            del admin_data[user_id]
                            return
                        if target_id in ADMIN_ID:
                            await update.message.reply_text("❌ لا يمكن حظر أدمن")
                            del admin_data[user_id]
                            return
                        d["target_user_id"] = target_id
                        d["target_username"] = user_found[1]
                        d["step"] = "confirm_ban"
                        keyboard = ReplyKeyboardMarkup([["✅ نعم، احظر", "❌ إلغاء"]], resize_keyboard=True)
                        await update.message.reply_text(
                            f"⚠️ هل أنت متأكد من حظر المستخدم؟\n\n"
                            f"🆔 معرف الحساب: `{target_id}`\n"
                            f"👤 اسم المستخدم: @{user_found[1] or 'بدون يوزر'}",
                            reply_markup=keyboard
                        )
                        return
                    except ValueError:
                        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                        return
                
                if d.get("step") == "confirm_ban":
                    if text == "✅ نعم، احظر":
                        cur.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (d["target_user_id"],))
                        conn.commit()
                        try:
                            await context.bot.send_message(d["target_user_id"], "⛔ لقد تم حظرك من استخدام البوت")
                        except:
                            pass
                        await update.message.reply_text(
                            f"✅ تم حظر المستخدم بنجاح\n\n"
                            f"🆔 معرف الحساب: `{d['target_user_id']}`\n"
                            f"👤 اسم المستخدم: @{d['target_username'] or 'بدون يوزر'}"
                        )
                    else:
                        await update.message.reply_text("❌ تم إلغاء الحظر")
                    del admin_data[user_id]
                    return
                
                # ===== فك حظر =====
                if d.get("step") == "unban_user":
                    if text == "إلغاء":
                        await update.message.reply_text("❌ تم الإلغاء")
                        del admin_data[user_id]
                        return
                    try:
                        target_id = int(text)
                        user_found = cur.execute("SELECT user_id, username FROM users WHERE user_id = ? AND is_banned = 1", (target_id,)).fetchone()
                        if not user_found:
                            await update.message.reply_text("❌ المستخدم غير محظور أو غير موجود")
                            del admin_data[user_id]
                            return
                        cur.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (target_id,))
                        conn.commit()
                        try:
                            await context.bot.send_message(target_id, "✅ تم فك الحظر عنك، يمكنك استخدام البوت الآن")
                        except:
                            pass
                        await update.message.reply_text(
                            f"✅ تم فك الحظر عن المستخدم\n\n"
                            f"🆔 معرف الحساب: `{target_id}`\n"
                            f"👤 اسم المستخدم: @{user_found[1] or 'بدون يوزر'}"
                        )
                    except ValueError:
                        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                        return
                    del admin_data[user_id]
                    return
                
                # ===== تعديل رسالة الدعم =====
                if d.get("step") == "edit_support":
                    d["new_support_text"] = text
                    cur.execute("UPDATE settings SET value = ? WHERE key = 'support_text'", (text,))
                    conn.commit()
                    await update.message.reply_text(
                        f"✅ تم تحديث رسالة الدعم الفني\n\n"
                        f"الرسالة القديمة:\n{d['old_support_text']}\n\n"
                        f"الرسالة الجديدة:\n{text}"
                    )
                    del admin_data[user_id]
                    return
                
                # ===== إضافة فئة رئيسية =====
                if d.get("step") == "add_main_category":
                    cat_name = text
                    try:
                        cur.execute("INSERT INTO categories (name, parent_id, level) VALUES (?, NULL, 1)", (cat_name,))
                        conn.commit()
                        await update.message.reply_text(f"✅ تم إضافة الفئة الرئيسية: {cat_name}")
                    except:
                        await update.message.reply_text("❌ حدث خطأ")
                    del admin_data[user_id]
                    return
                
                # ===== إضافة فئة فرعية - اختيار الأب =====
                if d.get("step") == "add_sub_select_parent":
                    try:
                        parent_id = int(text)
                        parent = cur.execute("SELECT name, level FROM categories WHERE id = ? AND is_product = 0", (parent_id,)).fetchone()
                        if not parent:
                            await update.message.reply_text("❌ الفئة غير موجودة أو هي منتج")
                            del admin_data[user_id]
                            return
                        d["parent_id"] = parent_id
                        d["parent_name"] = parent[0]
                        d["parent_level"] = parent[1]
                        d["step"] = "add_sub_name"
                        await update.message.reply_text(f"📝 إضافة فئة فرعية إلى: {parent[0]}\n\nأدخل اسم الفئة الفرعية:")
                        return
                    except ValueError:
                        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                        return
                
                # ===== إضافة فئة فرعية - الاسم =====
                if d.get("step") == "add_sub_name":
                    sub_name = text
                    new_level = d["parent_level"] + 1
                    cur.execute("INSERT INTO categories (name, parent_id, level) VALUES (?, ?, ?)", 
                              (sub_name, d["parent_id"], new_level))
                    conn.commit()
                    await update.message.reply_text(
                        f"✅ تم إضافة الفئة الفرعية بنجاح!\n\n"
                        f"📦 الفئة الأم: {d['parent_name']}\n"
                        f"🏷 الفئة الجديدة: {sub_name}\n"
                        f"📊 المستوى: {new_level}"
                    )
                    del admin_data[user_id]
                    return
                
                # ===== إضافة منتج نهائي - اختيار الفئة =====
                if d.get("step") == "add_product_select_category":
                    try:
                        cat_id = int(text)
                        cat = cur.execute("SELECT name, level FROM categories WHERE id = ? AND is_product = 0", (cat_id,)).fetchone()
                        if not cat:
                            await update.message.reply_text("❌ الفئة غير موجودة")
                            del admin_data[user_id]
                            return
                        d["product_parent_id"] = cat_id
                        d["product_parent_name"] = cat[0]
                        d["step"] = "add_product_name"
                        await update.message.reply_text(f"📝 إضافة منتج إلى: {cat[0]}\n\nأدخل اسم المنتج:")
                        return
                    except ValueError:
                        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                        return
                
                # ===== إضافة منتج نهائي - الاسم =====
                if d.get("step") == "add_product_name":
                    d["product_name"] = text
                    d["step"] = "add_product_price"
                    await update.message.reply_text(f"🏷 اسم المنتج: {text}\n\n💰 أدخل سعر المنتج (بالدولار):")
                    return
                
                # ===== إضافة منتج نهائي - السعر =====
                if d.get("step") == "add_product_price":
                    try:
                        price = float(text)
                        if price <= 0:
                            await update.message.reply_text("⚠️ السعر يجب أن يكون أكبر من 0")
                            return
                        cur.execute("INSERT INTO categories (name, parent_id, level, price, is_product) VALUES (?, ?, ?, ?, 1)", 
                                  (d["product_name"], d["product_parent_id"], 99, price))
                        conn.commit()
                        await update.message.reply_text(
                            f"✅ تم إضافة المنتج بنجاح!\n\n"
                            f"📦 الفئة: {d['product_parent_name']}\n"
                            f"🏷 المنتج: {d['product_name']}\n"
                            f"💰 السعر: ${price:.2f}"
                        )
                    except ValueError:
                        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                        return
                    del admin_data[user_id]
                    return
                
                # ===== تعديل منتج - اختيار المنتج =====
                if d.get("step") == "edit_product_select":
                    try:
                        prod_id = int(text)
                        prod = cur.execute("SELECT id, name, price, parent_id FROM categories WHERE id = ? AND is_product = 1", (prod_id,)).fetchone()
                        if not prod:
                            await update.message.reply_text("❌ المنتج غير موجود")
                            del admin_data[user_id]
                            return
                        d["edit_product_id"] = prod[0]
                        d["edit_product_name"] = prod[1]
                        d["edit_product_price"] = prod[2]
                        d["edit_product_parent"] = prod[3]
                        
                        parent_name = cur.execute("SELECT name FROM categories WHERE id = ?", (prod[3],)).fetchone()
                        
                        msg = (
                            f"✏️ معلومات المنتج\n{'─' * 30}\n"
                            f"📦 الفئة: {parent_name[0] if parent_name else ''}\n"
                            f"🏷 الاسم: {prod[1]}\n"
                            f"💰 السعر: ${prod[2]:.2f}\n\n"
                            f"اختر ما تريد تعديله:"
                        )
                        keyboard = ReplyKeyboardMarkup([
                            ["✏️ تعديل الاسم", "💰 تعديل السعر"],
                            ["🔙 رجوع"]
                        ], resize_keyboard=True)
                        d["step"] = "edit_product_field"
                        await update.message.reply_text(msg, reply_markup=keyboard)
                        return
                    except ValueError:
                        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                        return
                
                # ===== تعديل منتج - اختيار الحقل =====
                if d.get("step") == "edit_product_field":
                    if text == "✏️ تعديل الاسم":
                        d["edit_field"] = "name"
                        await update.message.reply_text(f"الاسم الحالي: {d['edit_product_name']}\n\nأدخل الاسم الجديد:")
                        return
                    if text == "💰 تعديل السعر":
                        d["edit_field"] = "price"
                        await update.message.reply_text(f"السعر الحالي: ${d['edit_product_price']:.2f}\n\nأدخل السعر الجديد:")
                        return
                    if text == "🔙 رجوع":
                        del admin_data[user_id]
                        await start(update, context)
                        return
                    
                    if d.get("edit_field") == "name":
                        new_name = text
                        cur.execute("UPDATE categories SET name = ? WHERE id = ?", (new_name, d["edit_product_id"]))
                        conn.commit()
                        await update.message.reply_text(f"✅ تم تعديل اسم المنتج\n\nالقديم: {d['edit_product_name']}\nالجديد: {new_name}")
                        del admin_data[user_id]
                        return
                    
                    if d.get("edit_field") == "price":
                        try:
                            new_price = float(text)
                            if new_price <= 0:
                                await update.message.reply_text("⚠️ السعر يجب أن يكون أكبر من 0")
                                return
                            cur.execute("UPDATE categories SET price = ? WHERE id = ?", (new_price, d["edit_product_id"]))
                            conn.commit()
                            await update.message.reply_text(f"✅ تم تعديل سعر المنتج\n\nالقديم: ${d['edit_product_price']:.2f}\nالجديد: ${new_price:.2f}")
                        except ValueError:
                            await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                            return
                        del admin_data[user_id]
                        return
                    return
                
                # ===== حالة الفئات - عرض القائمة =====
                if d.get("step") == "toggle_category_list":
                    try:
                        cat_id = int(text)
                        cat = cur.execute("SELECT id, name, is_active FROM categories WHERE id = ?", (cat_id,)).fetchone()
                        if not cat:
                            await update.message.reply_text("❌ الفئة غير موجودة")
                            del admin_data[user_id]
                            return
                        d["toggle_cat_id"] = cat[0]
                        d["toggle_cat_name"] = cat[1]
                        d["toggle_current"] = cat[2]
                        d["step"] = "toggle_category_confirm"
                        
                        status_text = "✅ مفعلة" if cat[2] == 1 else "⛔ معطلة"
                        action = "توقيف" if cat[2] == 1 else "تفعيل"
                        
                        keyboard = ReplyKeyboardMarkup([["✅ نعم", "❌ لا"]], resize_keyboard=True)
                        await update.message.reply_text(
                            f"🔄 حالة الفئة\n{'─' * 30}\n\n"
                            f"📦 الفئة: {cat[1]}\n"
                            f"📌 الحالة: {status_text}\n\n"
                            f"⚠️ هل تريد {action} هذه الفئة؟",
                            reply_markup=keyboard
                        )
                        return
                    except ValueError:
                        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                        del admin_data[user_id]
                        return
                
                # ===== حالة الفئات - تأكيد =====
                if d.get("step") == "toggle_category_confirm":
                    if text == "✅ نعم":
                        new_status = 0 if d["toggle_current"] == 1 else 1
                        cur.execute("UPDATE categories SET is_active = ? WHERE id = ?", (new_status, d["toggle_cat_id"]))
                        conn.commit()
                        status_text = "✅ مفعلة" if new_status == 1 else "⛔ معطلة"
                        await update.message.reply_text(
                            f"✅ تم تحديث حالة الفئة\n\n"
                            f"📦 الفئة: {d['toggle_cat_name']}\n"
                            f"📌 الحالة الجديدة: {status_text}"
                        )
                    else:
                        await update.message.reply_text("❌ تم الإلغاء")
                    del admin_data[user_id]
                    return
                
                # ===== حذف فئة =====
                if d.get("step") == "delete_category":
                    try:
                        cat_id = int(text)
                        cat = cur.execute("SELECT name FROM categories WHERE id = ?", (cat_id,)).fetchone()
                        if not cat:
                            await update.message.reply_text("❌ الفئة غير موجودة")
                            del admin_data[user_id]
                            return
                        cur.execute("DELETE FROM categories WHERE id = ? OR parent_id = ?", (cat_id, cat_id))
                        conn.commit()
                        await update.message.reply_text(f"✅ تم حذف الفئة: {cat[0]} وجميع الفئات التابعة لها")
                    except ValueError:
                        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                    del admin_data[user_id]
                    return
                
                # ===== تعديل حساب =====
                if d.get("step") == "edit_account_select":
                    try:
                        acc_id = int(text)
                        account = cur.execute("SELECT * FROM accounts WHERE id = ?", (acc_id,)).fetchone()
                        if not account:
                            await update.message.reply_text("❌ الحساب غير موجود")
                            del admin_data[user_id]
                            return
                        d["edit_acc_id"] = acc_id
                        d["edit_acc_data"] = {
                            "level": account[1], "likes": account[2], "prime": account[3],
                            "evo": account[4], "dances": account[5], "link_type": account[6],
                            "recovery": account[7], "price": account[8], "acc_type": account[9],
                            "images": account[10], "account_info": account[12] if len(account) > 12 else ""
                        }
                        
                        msg = (
                            f"✏️ معلومات الحساب #{acc_id}\n{'─' * 30}\n"
                            f"📊 اللفل: {account[1]}\n❤️ اللايكات: {account[2]}\n"
                            f"👑 البرايم: {account[3]}\n⚔️ الإيفو: {account[4]}\n"
                            f"💃 الرقصات: {account[5]}\n🔗 الربط: {account[6]}\n"
                            f"♻️ استعادة: {account[7]}\n💰 السعر: ${account[8]:.2f}\n"
                            f"📦 النوع: {account[9]}\n📝 معلومات الحساب: {account[12] if len(account) > 12 else 'لا يوجد'}"
                        )
                        keyboard = ReplyKeyboardMarkup([
                            ["📊 اللفل", "❤️ اللايكات"], ["👑 البرايم", "⚔️ الإيفو"],
                            ["💃 الرقصات", "🔗 الربط"], ["♻️ استعادة", "💰 السعر"],
                            ["📦 النوع", "📝 معلومات الحساب"], ["💾 حفظ التعديلات", "🔙 رجوع"]
                        ], resize_keyboard=True)
                        d["step"] = "edit_account_field"
                        await update.message.reply_text(msg + "\n\nاختر الحقل الذي تريد تعديله:", reply_markup=keyboard)
                        return
                    except ValueError:
                        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                        return
                
                if d.get("step") == "edit_account_field":
                    field_map = {
                        "📊 اللفل": "level", "❤️ اللايكات": "likes", "👑 البرايم": "prime",
                        "⚔️ الإيفو": "evo", "💃 الرقصات": "dances", "🔗 الربط": "link_type",
                        "♻️ استعادة": "recovery", "💰 السعر": "price", "📦 النوع": "acc_type",
                        "📝 معلومات الحساب": "account_info"
                    }
                    
                    if text == "💾 حفظ التعديلات":
                        data = d["edit_acc_data"]
                        cur.execute("""
                        UPDATE accounts SET level=?, likes=?, prime=?, evo=?, dances=?, 
                        link_type=?, recovery=?, price=?, acc_type=?, account_info=?
                        WHERE id=?
                        """, (data["level"], data["likes"], data["prime"], data["evo"], data["dances"],
                              data["link_type"], data["recovery"], data["price"], data["acc_type"],
                              data["account_info"], d["edit_acc_id"]))
                        conn.commit()
                        channel_updated = await update_channel_message(context, d["edit_acc_id"], data)
                        if channel_updated:
                            await update.message.reply_text(f"✅ تم حفظ تعديلات الحساب #{d['edit_acc_id']} وتحديث القناة")
                        else:
                            await update.message.reply_text(f"✅ تم حفظ تعديلات الحساب #{d['edit_acc_id']} (فشل تحديث القناة)")
                        del admin_data[user_id]
                        return
                    
                    if text == "🔙 رجوع":
                        del admin_data[user_id]
                        await start(update, context)
                        return
                    
                    if text in field_map:
                        d["editing_field"] = field_map[text]
                        if text == "📦 النوع":
                            await update.message.reply_text("اختر النوع الجديد:", reply_markup=ReplyKeyboardMarkup([["🔥 احترافي"], ["💎 نادر"], ["🟢 عادي"]], resize_keyboard=True))
                            return
                        await update.message.reply_text(f"أدخل القيمة الجديدة لـ {text}:")
                        return
                    
                    field = d.get("editing_field")
                    if field:
                        if field == "acc_type":
                            clean = text.replace("🔥", "").replace("💎", "").replace("🟢", "").strip()
                            if "احترافي" in clean:
                                d["edit_acc_data"]["acc_type"] = "احترافي"
                            elif "نادر" in clean:
                                d["edit_acc_data"]["acc_type"] = "نادر"
                            elif "عادي" in clean:
                                d["edit_acc_data"]["acc_type"] = "عادي"
                            else:
                                await update.message.reply_text("⚠️ الرجاء اختيار نوع من الأزرار")
                                return
                        else:
                            try:
                                if field in ["level", "likes", "prime", "evo", "dances"]:
                                    val = int(text)
                                    if field == "level" and (val < 20 or val > 100):
                                        await update.message.reply_text("⚠️ اللفل يجب أن يكون بين 20 و 100")
                                        return
                                    if field == "prime" and (val < 1 or val > 8):
                                        await update.message.reply_text("⚠️ البرايم يجب أن يكون بين 1 و 8")
                                        return
                                    if field == "evo" and (val < 0 or val > 20):
                                        await update.message.reply_text("⚠️ الإيفو يجب أن يكون بين 0 و 20")
                                        return
                                    d["edit_acc_data"][field] = val
                                elif field == "price":
                                    d["edit_acc_data"][field] = float(text)
                                else:
                                    d["edit_acc_data"][field] = text
                            except ValueError:
                                await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                                return
                        await update.message.reply_text(f"✅ تم تحديث الحقل. اختر حقل آخر أو اضغط '💾 حفظ التعديلات'")
                        d["editing_field"] = None
                    return
                
                if d["step"] == "level":
                    try:
                        level = int(text)
                        if level < 20 or level > 100:
                            await update.message.reply_text("⚠️ اللفل يجب أن يكون بين 20 و 100")
                            return
                        d["level"] = level; d["step"] = "likes"
                        await update.message.reply_text("❤️ أدخل اللايكات:")
                    except:
                        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                    return

                if d["step"] == "likes":
                    try:
                        d["likes"] = int(text); d["step"] = "prime"
                        await update.message.reply_text("👑 أدخل البرايم (من 1 إلى 8):")
                    except:
                        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                    return

                if d["step"] == "prime":
                    try:
                        prime = int(text)
                        if prime < 1 or prime > 8:
                            await update.message.reply_text("⚠️ البرايم يجب أن يكون بين 1 و 8")
                            return
                        d["prime"] = prime; d["step"] = "evo"
                        await update.message.reply_text("⚔️ أدخل الإيفو (من 0 إلى 20):")
                    except:
                        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                    return

                if d["step"] == "evo":
                    try:
                        evo = int(text)
                        if evo < 0 or evo > 20:
                            await update.message.reply_text("⚠️ الإيفو يجب أن يكون بين 0 و 20")
                            return
                        d["evo"] = evo; d["step"] = "dances"
                        await update.message.reply_text("💃 أدخل الرقصات:")
                    except:
                        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                    return

                if d["step"] == "dances":
                    try:
                        d["dances"] = int(text); d["step"] = "link"
                        await update.message.reply_text("🔗 نوع الربط (مثال: جوجل، فيسبوك):")
                    except:
                        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                    return

                if d["step"] == "link":
                    d["link_type"] = text; d["step"] = "recovery"
                    await update.message.reply_text("♻️ هل يوجد استعادة؟ (نعم/لا):")
                    return

                if d["step"] == "recovery":
                    d["recovery"] = text; d["step"] = "price"
                    await update.message.reply_text("💰 السعر (بالدولار):")
                    return

                if d["step"] == "price":
                    try:
                        d["price"] = float(text); d["step"] = "type"
                        await update.message.reply_text("📦 اختر نوع الحساب:", reply_markup=ReplyKeyboardMarkup([["🔥 احترافي"], ["💎 نادر"], ["🟢 عادي"]], resize_keyboard=True))
                    except:
                        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                    return

                if d["step"] == "type":
                    clean = text.replace("🔥", "").replace("💎", "").replace("🟢", "").strip()
                    if "احترافي" in clean:
                        d["acc_type"] = "احترافي"
                    elif "نادر" in clean:
                        d["acc_type"] = "نادر"
                    elif "عادي" in clean:
                        d["acc_type"] = "عادي"
                    else:
                        await update.message.reply_text("⚠️ الرجاء اختيار نوع من الأزرار")
                        return
                    d["step"] = "images"
                    await update.message.reply_text("📸 أرسل الصورة الأولى من 3 صور للحساب:")
                    return
                
                if d.get("step") == "account_info":
                    d["account_info"] = text
                    cur.execute("""
                    INSERT INTO accounts (level, likes, prime, evo, dances, link_type, recovery, price, acc_type, images, account_info)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (d["level"], d["likes"], d["prime"], d["evo"], d["dances"], 
                          d["link_type"], d["recovery"], d["price"], d["acc_type"], ",".join(d["images"]), d["account_info"]))
                    conn.commit()
                    acc_id = cur.lastrowid
                    
                    try:
                        caption = (
                            f"🎮 حساب #{acc_id}\n{'─' * 30}\n"
                            f"📊 • اللفل: {d['level']}\n❤️ • اللايكات: {d['likes']}\n"
                            f"👑 • البرايم: {d['prime']}\n⚔️ • الإيفو: {d['evo']}\n"
                            f"💃 • الرقصات: {d['dances']}\n🔗 • الربط: {d['link_type']}\n"
                            f"♻️ • استعادة: {d['recovery']}\n📦 • النوع: {d['acc_type']}\n"
                            f"💰 • السعر: {d['price']}$"
                        )
                        media = []
                        for i, img in enumerate(d["images"]):
                            if i == 0:
                                media.append(InputMediaPhoto(media=img, caption=caption))
                            else:
                                media.append(InputMediaPhoto(media=img))
                        sent_messages = await context.bot.send_media_group(CHANNEL, media)
                        all_msg_ids = ",".join([str(msg.message_id) for msg in sent_messages])
                        cur.execute("UPDATE accounts SET channel_msg_ids = ? WHERE id = ?", (all_msg_ids, acc_id))
                        conn.commit()
                        await update.message.reply_text(f"✅ تم إضافة الحساب #{acc_id} وإرساله للقناة بنجاح")
                    except Exception as e:
                        print(f"Error sending to channel: {e}")
                        await update.message.reply_text(f"✅ تم إضافة الحساب #{acc_id} (فشل إرسال القناة)")
                    
                    del admin_data[user_id]
                    return

                # ===== إضافة طريقة دفع - الاسم =====
                if d.get("step") == "add_payment_name":
                    d["payment_name"] = text
                    d["step"] = "add_payment_desc"
                    await update.message.reply_text("📩 أدخل وصف طريقة الدفع:")
                    return
                
                # ===== إضافة طريقة دفع - الوصف =====
                if d.get("step") == "add_payment_desc":
                    d["payment_desc"] = text
                    d["step"] = "add_payment_currency"
                    keyboard = ReplyKeyboardMarkup([["🇸🇾 سورية", "💵 دولار"]], resize_keyboard=True)
                    await update.message.reply_text(
                        f"💱 هل هذه الطريقة بالعملة السورية أم الدولار؟\n\n"
                        f"📌 الاسم: {d['payment_name']}\n"
                        f"📝 الوصف: {text}",
                        reply_markup=keyboard
                    )
                    return
                
                # ===== إضافة طريقة دفع - اختيار العملة =====
                if d.get("step") == "add_payment_currency":
                    if text == "🇸🇾 سورية":
                        try:
                            cur.execute("INSERT INTO payment_methods (name, description, currency, exchange_rate) VALUES (?, ?, ?, ?)", 
                                      (d["payment_name"], d["payment_desc"], "SYP", 1))
                            conn.commit()
                            await update.message.reply_text(
                                f"✅ تم إضافة طريقة الدفع بنجاح!\n\n"
                                f"📌 الاسم: {d['payment_name']}\n"
                                f"📝 الوصف: {d['payment_desc']}\n"
                                f"💱 العملة: ليرة سورية\n\n"
                                f"⚠️ لا تنسى تحديد سعر الصرف من: 💱 سعر الصرف"
                            )
                        except:
                            await update.message.reply_text("❌ هذه الطريقة موجودة بالفعل")
                    elif text == "💵 دولار":
                        try:
                            cur.execute("INSERT INTO payment_methods (name, description, currency, exchange_rate) VALUES (?, ?, ?, ?)", 
                                      (d["payment_name"], d["payment_desc"], "USD", 1))
                            conn.commit()
                            await update.message.reply_text(
                                f"✅ تم إضافة طريقة الدفع بنجاح!\n\n"
                                f"📌 الاسم: {d['payment_name']}\n"
                                f"📝 الوصف: {d['payment_desc']}\n"
                                f"💱 العملة: دولار أمريكي"
                            )
                        except:
                            await update.message.reply_text("❌ هذه الطريقة موجودة بالفعل")
                    else:
                        await update.message.reply_text("⚠️ الرجاء اختيار العملة من الأزرار")
                        return
                    del admin_data[user_id]
                    return
                
                # ===== سعر الصرف - إدخال السعر =====
                if d.get("step") == "exchange_rate_value":
                    try:
                        rate = float(text)
                        if rate <= 0:
                            await update.message.reply_text("⚠️ السعر يجب أن يكون أكبر من 0")
                            return
                        d["exchange_rate"] = rate
                        methods = cur.execute("SELECT id, name FROM payment_methods WHERE currency = 'SYP'").fetchall()
                        if not methods:
                            await update.message.reply_text("❌ لا توجد طرق دفع بالعملة السورية")
                            del admin_data[user_id]
                            return
                        keyboard = [[f"{m[1]}"] for m in methods]
                        d["step"] = "exchange_rate_select_method"
                        await update.message.reply_text(
                            f"💱 سعر الصرف: {rate}\n\n"
                            f"اختر طريقة الدفع لربط هذا السعر بها:",
                            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                        )
                        return
                    except ValueError:
                        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                        return
                
                # ===== سعر الصرف - اختيار الطريقة =====
                if d.get("step") == "exchange_rate_select_method":
                    method_name = text.strip()
                    method = cur.execute("SELECT id, name FROM payment_methods WHERE name = ? AND currency = 'SYP'", (method_name,)).fetchone()
                    if not method:
                        await update.message.reply_text("❌ طريقة الدفع غير موجودة")
                        del admin_data[user_id]
                        return
                    cur.execute("UPDATE payment_methods SET exchange_rate = ? WHERE id = ?", (d["exchange_rate"], method[0]))
                    conn.commit()
                    await update.message.reply_text(
                        f"✅ تم تحديد سعر الصرف\n\n"
                        f"💱 {d['exchange_rate']} ل.س = $1\n"
                        f"💳 طريقة الدفع: {method_name}"
                    )
                    del admin_data[user_id]
                    return
                
                # ===== تعديل سعر الصرف - اختيار الطريقة =====
                if d.get("step") == "edit_exchange_rate_select":
                    method_name = text.strip()
                    method = cur.execute("SELECT id, name, exchange_rate FROM payment_methods WHERE name = ? AND currency = 'SYP'", (method_name,)).fetchone()
                    if not method:
                        await update.message.reply_text("❌ طريقة الدفع غير موجودة")
                        del admin_data[user_id]
                        return
                    d["edit_method_id"] = method[0]
                    d["edit_method_name"] = method[1]
                    d["old_rate"] = method[2]
                    d["step"] = "edit_exchange_rate_value"
                    await update.message.reply_text(
                        f"✏️ تعديل سعر الصرف\n\n"
                        f"💳 طريقة الدفع: {method[1]}\n"
                        f"💰 السعر الحالي: {method[2]} ل.س = $1\n\n"
                        f"أدخل السعر الجديد:"
                    )
                    return
                
                # ===== تعديل سعر الصرف - القيمة الجديدة =====
                if d.get("step") == "edit_exchange_rate_value":
                    try:
                        new_rate = float(text)
                        if new_rate <= 0:
                            await update.message.reply_text("⚠️ السعر يجب أن يكون أكبر من 0")
                            return
                        cur.execute("UPDATE payment_methods SET exchange_rate = ? WHERE id = ?", (new_rate, d["edit_method_id"]))
                        conn.commit()
                        await update.message.reply_text(
                            f"✅ تم تعديل سعر الصرف\n\n"
                            f"💳 طريقة الدفع: {d['edit_method_name']}\n"
                            f"💰 القديم: {d['old_rate']} ل.س\n"
                            f"💰 الجديد: {new_rate} ل.س"
                        )
                    except ValueError:
                        await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                        return
                    del admin_data[user_id]
                    return
                
                if d.get("step") == "edit_payment_select":
                    d["edit_payment_name"] = text; d["step"] = "edit_payment_new_desc"
                    await update.message.reply_text(f"📩 الوصف الجديد لـ: {text}:")
                    return
                
                if d.get("step") == "edit_payment_new_desc":
                    cur.execute("UPDATE payment_methods SET description = ? WHERE name = ?", (text, d["edit_payment_name"]))
                    conn.commit()
                    await update.message.reply_text("✅ تم التعديل")
                    del admin_data[user_id]
                    return
                
                if d.get("step") == "delete_payment_select":
                    cur.execute("DELETE FROM payment_methods WHERE name = ?", (text,))
                    conn.commit()
                    await update.message.reply_text("✅ تم الحذف")
                    del admin_data[user_id]
                    return

        # ============ أزرار الأدمن ============
        if user_id in ADMIN_ID:
            if text == "📊 لوحة الأدمن":
                keyboard = [
                    ["➕ إضافة حساب", "🗑 حذف حساب"],
                    ["✏️ تعديل حساب", "📋 قائمة الحسابات"],
                    ["💳 إدارة طرق الدفع", "👥 المستخدمين"],
                    ["📊 الإحصائيات", "📋 طلبات الرصيد"],
                    ["📢 إرسال إذاعة", "💰 تعديل رصيد"],
                    ["🚫 حظر مستخدم", "✅ فك حظر مستخدم"],
                    ["📋 المحظورين", "✏️ تعديل رسالة الدعم"],
                    ["🎮 إدارة الفئات", "🔙 رجوع"]
                ]
                await update.message.reply_text("📊 لوحة الأدمن", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
                return
            
            if text == "🎮 إدارة الفئات":
                keyboard = [
                    ["➕ إضافة فئة رئيسية", "➕ إضافة فئة فرعية"],
                    ["➕ إضافة منتج نهائي", "✏️ تعديل منتج"],
                    ["🗑 حذف فئة", "🔄 حالة الفئات"],
                    ["📋 عرض شجرة الفئات", "🔙 رجوع"]
                ]
                await update.message.reply_text("🎮 لوحة إدارة الفئات", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
                return
            
            if text == "➕ إضافة فئة رئيسية":
                admin_data[user_id] = {"step": "add_main_category"}
                await update.message.reply_text("📩 أدخل اسم الفئة الرئيسية:\n(مثال: تطبيقات، ألعاب، بطاقات)")
                return
            
            if text == "➕ إضافة فئة فرعية":
                categories = cur.execute("SELECT id, name, level FROM categories WHERE is_product = 0 ORDER BY level, id").fetchall()
                if not categories:
                    await update.message.reply_text("❌ لا توجد فئات، أضف فئة رئيسية أولاً")
                    return
                msg = "📦 اختر رقم الفئة الأم:\n\n"
                for c in categories:
                    level_name = "رئيسية" if c[2] == 1 else "فرعية" if c[2] == 2 else "نهائية"
                    msg += f"{c[0]}. {c[1]} ({level_name})\n"
                admin_data[user_id] = {"step": "add_sub_select_parent"}
                await update.message.reply_text(msg)
                return
            
            if text == "➕ إضافة منتج نهائي":
                categories = cur.execute("SELECT id, name, level FROM categories WHERE is_product = 0 ORDER BY level, id").fetchall()
                if not categories:
                    await update.message.reply_text("❌ لا توجد فئات")
                    return
                msg = "📦 اختر رقم الفئة لإضافة المنتج:\n\n"
                for c in categories:
                    level_name = "رئيسية" if c[2] == 1 else "فرعية" if c[2] == 2 else "نهائية"
                    msg += f"{c[0]}. {c[1]} ({level_name})\n"
                admin_data[user_id] = {"step": "add_product_select_category"}
                await update.message.reply_text(msg)
                return
            
            if text == "✏️ تعديل منتج":
                products = cur.execute("SELECT c.id, c.name, c.price, p.name FROM categories c JOIN categories p ON c.parent_id = p.id WHERE c.is_product = 1 ORDER BY c.id").fetchall()
                if not products:
                    await update.message.reply_text("❌ لا توجد منتجات")
                    return
                msg = "✏️ اختر رقم المنتج للتعديل:\n\n"
                for p in products:
                    msg += f"{p[0]}. {p[1]} - ${p[2]:.2f} (في {p[3]})\n"
                admin_data[user_id] = {"step": "edit_product_select"}
                await update.message.reply_text(msg)
                return
            
            if text == "🗑 حذف فئة":
                categories = cur.execute("SELECT id, name, level, is_product FROM categories ORDER BY level, id").fetchall()
                if not categories:
                    await update.message.reply_text("❌ لا توجد فئات")
                    return
                msg = "🗑 اختر رقم الفئة للحذف:\n\n⚠️ سيتم حذف كل الفئات التابعة لها\n\n"
                for c in categories:
                    type_name = "منتج" if c[3] == 1 else ("رئيسية" if c[2] == 1 else "فرعية" if c[2] == 2 else "نهائية")
                    msg += f"{c[0]}. {c[1]} ({type_name})\n"
                admin_data[user_id] = {"step": "delete_category"}
                await update.message.reply_text(msg)
                return
            
            if text == "🔄 حالة الفئات":
                categories = cur.execute("SELECT id, name, level, is_active, is_product FROM categories ORDER BY level, id").fetchall()
                if not categories:
                    await update.message.reply_text("❌ لا توجد فئات")
                    return
                msg = "🔄 اختر رقم الفئة لتغيير حالتها:\n\n"
                for c in categories:
                    type_name = "منتج" if c[4] == 1 else ("رئيسية" if c[2] == 1 else "فرعية")
                    status = "✅" if c[3] == 1 else "⛔"
                    msg += f"{c[0]}. {status} {c[1]} ({type_name})\n"
                admin_data[user_id] = {"step": "toggle_category_list"}
                await update.message.reply_text(msg)
                return
            
            if text == "📋 عرض شجرة الفئات":
                categories = cur.execute("SELECT id, name, parent_id, level, is_product, price, is_active FROM categories ORDER BY level, id").fetchall()
                if not categories:
                    await update.message.reply_text("❌ لا توجد فئات")
                    return
                
                msg = "📋 شجرة الفئات\n" + "─" * 30 + "\n\n"
                main_cats = [c for c in categories if c[2] is None]
                for mc in main_cats:
                    status_icon = "✅" if mc[6] == 1 else "⛔"
                    msg += f"{status_icon} 📦 {mc[1]} (رئيسية)\n"
                    subs = [c for c in categories if c[2] == mc[0] and c[4] == 0]
                    for sc in subs:
                        sc_status = "✅" if sc[6] == 1 else "⛔"
                        msg += f"   {sc_status} ├─ {sc[1]} (فرعية)\n"
                        items = [c for c in categories if c[2] == sc[0]]
                        for ic in items:
                            ic_status = "✅" if ic[6] == 1 else "⛔"
                            if ic[4] == 1:
                                msg += f"   │  {ic_status} └─ 🏷 {ic[1]} - ${ic[5]:.2f} (منتج)\n"
                            else:
                                msg += f"   │  {ic_status} └─ {ic[1]} (نهائية)\n"
                    direct_products = [c for c in categories if c[2] == mc[0] and c[4] == 1]
                    for dp in direct_products:
                        dp_status = "✅" if dp[6] == 1 else "⛔"
                        msg += f"   {dp_status} └─ 🏷 {dp[1]} - ${dp[5]:.2f} (منتج)\n"
                    msg += "\n"
                await update.message.reply_text(msg)
                return
            
            if text == "🔙 رجوع":
                if user_id in admin_data: del admin_data[user_id]
                if 'delete_mode' in context.user_data: del context.user_data['delete_mode']
                await start(update, context)
                return
            
            if text == "➕ إضافة حساب":
                admin_data[user_id] = {"step": "level", "images": []}
                await update.message.reply_text("📩 أدخل لفل الحساب (من 20 إلى 100):\n\n⚠️ الشروط:\n• اللفل: 20 - 100\n• البرايم: 1 - 8\n• الإيفو: 0 - 20")
                return
            
            if text == "🗑 حذف حساب":
                context.user_data['delete_mode'] = True
                await update.message.reply_text("📩 أرسل رقم الحساب للحذف:")
                return
            
            if text == "✏️ تعديل حساب":
                admin_data[user_id] = {"step": "edit_account_select"}
                await update.message.reply_text("📩 أرسل رقم الحساب الذي تريد تعديله:")
                return
            
            if text == "📋 قائمة الحسابات":
                accounts = cur.execute("SELECT id, acc_type, price, level FROM accounts ORDER BY id DESC").fetchall()
                if not accounts:
                    await update.message.reply_text("❌ لا توجد حسابات")
                    return
                total_value = sum(a[2] for a in accounts)
                msg = f"📋 قائمة الحسابات المتاحة\n{'─' * 30}\n📊 العدد: {len(accounts)} | 💰 القيمة الإجمالية: ${total_value:.2f}\n{'─' * 30}\n\n"
                for a in accounts:
                    acc_id, acc_type, price, level = a
                    emoji = "🔥" if "احترافي" in acc_type else "💎" if "نادر" in acc_type else "🟢"
                    msg += f"{emoji} #{acc_id} | {acc_type} | لفل {level} | {price}$\n"
                await update.message.reply_text(msg)
                return
            
            if text == "💳 إدارة طرق الدفع":
                keyboard = [
                    ["➕ إضافة طريقة دفع", "✏️ تعديل طريقة دفع"],
                    ["🗑 حذف طريقة دفع", "📋 قائمة طرق الدفع"],
                    ["💱 سعر الصرف", "✏️ تعديل سعر الصرف"],
                    ["🔙 رجوع"]
                ]
                await update.message.reply_text("💳 إدارة طرق الدفع", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
                return
            
            if text == "💱 سعر الصرف":
                admin_data[user_id] = {"step": "exchange_rate_value"}
                await update.message.reply_text("💱 أدخل سعر صرف الدولار مقابل الليرة السورية:\n\nمثال: 14000")
                return
            
            if text == "✏️ تعديل سعر الصرف":
                methods = cur.execute("SELECT name FROM payment_methods WHERE currency = 'SYP'").fetchall()
                if not methods:
                    await update.message.reply_text("❌ لا توجد طرق دفع بالعملة السورية")
                    return
                keyboard = [[m[0]] for m in methods]
                admin_data[user_id] = {"step": "edit_exchange_rate_select"}
                await update.message.reply_text("اختر طريقة الدفع لتعديل سعر الصرف:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
                return
            
            if text == "➕ إضافة طريقة دفع":
                admin_data[user_id] = {"step": "add_payment_name"}
                await update.message.reply_text("📩 أدخل اسم طريقة الدفع:")
                return
            
            if text == "✏️ تعديل طريقة دفع":
                methods = cur.execute("SELECT name FROM payment_methods").fetchall()
                if not methods:
                    await update.message.reply_text("❌ لا توجد")
                    return
                keyboard = [[m[0]] for m in methods] + [["🔙 رجوع"]]
                admin_data[user_id] = {"step": "edit_payment_select"}
                await update.message.reply_text("اختر طريقة", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
                return
            
            if text == "🗑 حذف طريقة دفع":
                methods = cur.execute("SELECT name FROM payment_methods").fetchall()
                if not methods:
                    await update.message.reply_text("❌ لا توجد")
                    return
                keyboard = [[m[0]] for m in methods] + [["🔙 رجوع"]]
                admin_data[user_id] = {"step": "delete_payment_select"}
                await update.message.reply_text("اختر طريقة", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
                return
            
            if text == "📋 قائمة طرق الدفع":
                methods = cur.execute("SELECT id, name, description, currency, exchange_rate FROM payment_methods").fetchall()
                if not methods:
                    await update.message.reply_text("❌ لا توجد")
                    return
                msg = "💳 طرق الدفع المتاحة\n\n"
                for m in methods:
                    currency_text = "ل.س" if m[3] == "SYP" else "$"
                    rate_text = f"\n💱 سعر الصرف: {m[4]} ل.س = $1" if m[3] == "SYP" else ""
                    msg += f"🆔 {m[0]}\n📌 {m[1]}\n📝 {m[2][:100]}...\n💱 العملة: {currency_text}{rate_text}\n{'─' * 30}\n\n"
                await update.message.reply_text(msg)
                return
            
            if text == "👥 المستخدمين":
                users = cur.execute("SELECT user_id, username, balance, total_spent, is_banned FROM users ORDER BY total_spent DESC").fetchall()
                if not users:
                    await update.message.reply_text("❌ لا يوجد مستخدمين")
                    return
                
                total_users = len(users)
                total_balance = sum(u[2] for u in users)
                total_spent = sum(u[3] for u in users)
                banned_count = sum(1 for u in users if u[4] == 1)
                
                msg = (
                    f"👥 قائمة المستخدمين\n{'─' * 30}\n"
                    f"📊 إحصائيات عامة:\n"
                    f"👤 عدد المستخدمين: {total_users}\n"
                    f"🚫 المحظورين: {banned_count}\n"
                    f"💰 إجمالي الأرصدة: ${total_balance:.2f}\n"
                    f"💸 إجمالي المشتريات: ${total_spent:.2f}\n"
                    f"{'─' * 30}\n\n"
                )
                
                for i, u in enumerate(users, 1):
                    uid, uname, bal, spent, banned = u
                    if spent >= 100:
                        rank = "💎 مميز"
                    elif spent >= 50:
                        rank = "⭐ نشط"
                    else:
                        rank = "🆕 جديد"
                    ban_icon = " ⛔ محظور" if banned == 1 else ""
                    
                    msg += (
                        f"{i}.\n"
                        f"🆔 معرف الحساب: `{uid}`\n"
                        f"👤 اسم المستخدم: @{uname or 'بدون يوزر'}\n"
                        f"💰 الرصيد: ${bal:.2f}\n"
                        f"💸 المشتريات: ${spent:.2f}\n"
                        f"🏅 التصنيف: {rank}{ban_icon}\n"
                        f"{'─' * 30}\n\n"
                    )
                await update.message.reply_text(msg)
                return
            
            if text == "📊 الإحصائيات":
                stats = cur.execute("SELECT acc_type, COUNT(*) FROM accounts GROUP BY acc_type").fetchall()
                users = cur.execute("SELECT COUNT(*) FROM users WHERE is_banned=0").fetchone()[0]
                banned = cur.execute("SELECT COUNT(*) FROM users WHERE is_banned=1").fetchone()[0]
                orders = cur.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
                completed_orders = cur.execute("SELECT COUNT(*) FROM orders WHERE status='completed'").fetchone()[0]
                pending_delivery = cur.execute("SELECT COUNT(*) FROM orders WHERE status='pending_delivery'").fetchone()[0]
                reserved = cur.execute("SELECT COUNT(*) FROM orders WHERE status='reserved'").fetchone()[0]
                pay = cur.execute("SELECT COUNT(*) FROM payment_methods").fetchone()[0]
                pend = cur.execute("SELECT COUNT(*) FROM balance_requests WHERE status='pending'").fetchone()[0]
                total_revenue = cur.execute("SELECT SUM(paid_amount) FROM orders WHERE status='completed'").fetchone()[0] or 0
                
                msg = (
                    f"📊 لوحة الإحصائيات\n{'─' * 30}\n\n"
                    f"👤 المستخدمين:\n"
                    f"   • المسجلين: {users}\n"
                    f"   • المحظورين: {banned}\n\n"
                    f"🛒 المبيعات:\n"
                    f"   • إجمالي الطلبات: {orders}\n"
                    f"   • ✅ مكتملة: {completed_orders}\n"
                    f"   • 📩 قيد التسليم: {pending_delivery}\n"
                    f"   • 📌 محجوزة: {reserved}\n"
                    f"   • 💰 إجمالي الأرباح: ${total_revenue:.2f}\n\n"
                    f"💳 طرق الدفع: {pay}\n\n"
                    f"💰 طلبات الرصيد المعلقة: {pend}\n\n"
                    f"🎮 الحسابات المتاحة: {sum(c for _,c in stats)}\n"
                )
                for t, c in stats:
                    msg += f"   • {t}: {c}\n"
                await update.message.reply_text(msg)
                return
            
            if text == "📋 طلبات الرصيد":
                reqs = cur.execute("SELECT id, user_id, username, amount, payment_method, transaction_number, status, date FROM balance_requests ORDER BY date DESC LIMIT 50").fetchall()
                if not reqs:
                    await update.message.reply_text("❌ لا توجد طلبات")
                    return
                
                pending = sum(1 for r in reqs if r[6] == 'pending')
                msg = f"📋 طلبات الرصيد\n{'─' * 30}\n📊 ملخص: ⏳ {pending}\n{'─' * 30}\n\n"
                for r in reqs:
                    req_id, uid, uname, amount, method, trans_num, status, date = r
                    emoji = "✅" if status == "approved" else "❌" if status == "rejected" else "⏳"
                    status_text = "مقبول" if status == "approved" else "مرفوض" if status == "rejected" else "قيد الانتظار"
                    msg += (
                        f"🆔 طلب #{req_id} {emoji}\n"
                        f"👤 المستخدم: @{uname or uid}\n"
                        f"💰 المبلغ: ${amount:.2f}\n"
                        f"💳 طريقة الدفع: {method}\n"
                        f"🔢 رقم العملية: {trans_num or 'لا يوجد'}\n"
                        f"📌 الحالة: {status_text}\n"
                        f"📅 التاريخ: {date[:16]}\n"
                        f"{'─' * 30}\n\n"
                    )
                await update.message.reply_text(msg)
                return
            
            if text == "📢 إرسال إذاعة":
                admin_data[user_id] = {"step": "broadcast"}
                await update.message.reply_text("📢 إرسال رسالة للجميع\n\nأرسل الرسالة التي تريد إرسالها لجميع مستخدمي البوت:\n(يمكنك استخدام النصوص والرموز التعبيرية)\n\nللإلغاء أرسل: إلغاء")
                return
            
            if text == "💰 تعديل رصيد":
                admin_data[user_id] = {"step": "modify_balance_user"}
                await update.message.reply_text("💰 تعديل رصيد مستخدم\n\nأرسل معرف المستخدم (اليوزر):\nمثال: @username أو 123456789\n\nللإلغاء أرسل: إلغاء")
                return
            
            if text == "🚫 حظر مستخدم":
                admin_data[user_id] = {"step": "ban_user"}
                await update.message.reply_text("🚫 حظر مستخدم\n\nأرسل معرف المستخدم (ID) للحظر:\nمثال: 123456789\n\nللإلغاء أرسل: إلغاء")
                return
            
            if text == "✅ فك حظر مستخدم":
                admin_data[user_id] = {"step": "unban_user"}
                await update.message.reply_text("✅ فك حظر مستخدم\n\nأرسل معرف المستخدم (ID) لفك الحظر:\nمثال: 123456789\n\nللإلغاء أرسل: إلغاء")
                return
            
            if text == "📋 المحظورين":
                banned_users = cur.execute("SELECT user_id, username FROM users WHERE is_banned=1").fetchall()
                if not banned_users:
                    await update.message.reply_text("✅ لا يوجد مستخدمين محظورين")
                    return
                msg = f"🚫 قائمة المحظورين\n{'─' * 30}\nالعدد: {len(banned_users)}\n\n"
                for u in banned_users:
                    msg += f"🆔 `{u[0]}` | 👤 @{u[1] or 'بدون يوزر'}\n"
                await update.message.reply_text(msg)
                return
            
            if text == "✏️ تعديل رسالة الدعم":
                old_text = get_support_text()
                admin_data[user_id] = {"step": "edit_support", "old_support_text": old_text}
                await update.message.reply_text(
                    f"📝 رسالة الدعم الحالية:\n\n{old_text}\n\n{'─' * 30}\n\n"
                    f"أرسل رسالة الدعم الجديدة:\n(تقدر تستخدم إيموجي وروابط ويوزرات)\n\n"
                    f"مثال:\n📞 للتواصل: @username\n💬 أو عبر الرابط: t.me/username"
                )
                return

        # ============ أزرار المستخدمين ============
        if text == "🛍 المنتجات":
            categories = cur.execute("SELECT id, name FROM categories WHERE parent_id IS NULL ORDER BY id").fetchall()
            if not categories:
                await update.message.reply_text("❌ لا توجد فئات حالياً")
                return
            
            msg = (
                f"🛍 • المنتجات المتاحة\n"
                f"━━━━━━━━━━━━━━━━━━━\n\n"
                f"اختر الفئة اللي بدك تتصفحها:\n"
            )
            keyboard = []
            row = []
            for c in categories:
                row.append(InlineKeyboardButton(f"{c[1]}", callback_data=f"cat_{c[0]}"))
                if len(row) == 2:
                    keyboard.append(row)
                    row = []
            if row:
                keyboard.append(row)
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
            return
        
        if text.startswith("🎮 عرض الحسابات"):
            cur.execute("SELECT acc_type, COUNT(*) FROM accounts GROUP BY acc_type")
            counts = {row[0]: row[1] for row in cur.fetchall()}
            keyboard = [
                [f"🔥 احترافي ({counts.get('احترافي', 0)})", f"💎 نادر ({counts.get('نادر', 0)})"],
                [f"🟢 عادي ({counts.get('عادي', 0)})", "🔙 رجوع"]
            ]
            await update.message.reply_text("🎮 اختر نوع الحسابات التي تريد عرضها:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
            return
        
        if text.startswith("🔥 احترافي"):
            await send_accounts(update, cur.execute("SELECT * FROM accounts WHERE acc_type='احترافي' ORDER BY id DESC").fetchall())
            return
        
        if text.startswith("💎 نادر"):
            await send_accounts(update, cur.execute("SELECT * FROM accounts WHERE acc_type='نادر' ORDER BY id DESC").fetchall())
            return
        
        if text.startswith("🟢 عادي"):
            await send_accounts(update, cur.execute("SELECT * FROM accounts WHERE acc_type='عادي' ORDER BY id DESC").fetchall())
            return
        
        if text == "💰 إضافة رصيد":
            methods = cur.execute("SELECT name FROM payment_methods").fetchall()
            if not methods:
                await update.message.reply_text("❌ لا توجد طرق دفع")
                return
            keyboard = [[f"💳 {m[0]}"] for m in methods] + [["🔙 رجوع"]]
            await update.message.reply_text("💰 اختر طريقة الدفع:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
            return
        
        if text == "👤 حسابي":
            u = cur.execute("SELECT user_id, username, balance, total_spent FROM users WHERE user_id=?", (user_id,)).fetchone()
            if not u:
                await update.message.reply_text("❌ غير موجود")
                return
            orders = cur.execute("SELECT COUNT(*) FROM orders WHERE user_id=?", (user_id,)).fetchone()[0]
            completed_orders = cur.execute("SELECT COUNT(*) FROM orders WHERE user_id=? AND status='completed'", (user_id,)).fetchone()[0]
            reserved_orders = cur.execute("SELECT COUNT(*) FROM orders WHERE user_id=? AND status='reserved'", (user_id,)).fetchone()[0]
            msg = (
                f"👤 معلومات حسابك الشخصي\n{'─' * 30}\n\n"
                f"🆔 معرف الحساب: `{u[0]}`\n"
                f"📛 اسم المستخدم: @{u[1] or 'بدون يوزر'}\n"
                f"💰 الرصيد الحالي: ${u[2]:.2f}\n"
                f"💸 إجمالي المشتريات: ${u[3]:.2f}\n\n"
                f"📊 إحصائيات طلباتك:\n"
                f"📦 إجمالي الطلبات: {orders}\n"
                f"✅ طلبات مكتملة: {completed_orders}\n"
                f"📌 حجوزات نشطة: {reserved_orders}\n\n"
                f"💡 للاستفسار: @AXS_Admin"
            )
            await update.message.reply_text(msg)
            return
        
        if text == "📞 الدعم الفني":
            support_text = get_support_text()
            await update.message.reply_text(support_text)
            return
        
        if text.startswith("💳 "):
            method = text.replace("💳 ", "").strip()
            res = cur.execute("SELECT name, description, currency, exchange_rate FROM payment_methods WHERE name=?", (method,)).fetchone()
            if res:
                currency_text = "بالليرة السورية" if res[2] == "SYP" else "بالدولار"
                user_data[user_id] = {
                    "payment_method": res[0],
                    "is_syp": res[2] == "SYP",
                    "exchange_rate": res[3] if res[2] == "SYP" else 1
                }
                await update.message.reply_text(
                    f"💳 {res[0]}\n"
                    f"{'─' * 30}\n"
                    f"{res[1]}\n\n"
                    f"💱 العملة: {currency_text}\n\n"
                    f"📩 أرسل المبلغ {currency_text}:"
                )
                return
            else:
                await update.message.reply_text("❌ غير موجودة")
                return
        
        if text == "🔙 رجوع":
            if user_id in user_data: del user_data[user_id]
            await start(update, context)
            return
        
        if user_id in user_data and "payment_method" in user_data[user_id]:
            d = user_data[user_id]
            
            if d.get("is_syp") and "amount_syp" not in d:
                try:
                    amount_syp = float(text)
                    if amount_syp <= 0:
                        await update.message.reply_text("⚠️ يجب أن يكون المبلغ أكبر من 0")
                        return
                    d["amount_syp"] = amount_syp
                    exchange_rate = d.get("exchange_rate", 1)
                    amount_usd = round(amount_syp / exchange_rate, 2)
                    d["amount"] = amount_usd
                    await update.message.reply_text(
                        f"💱 تم تحويل المبلغ:\n\n"
                        f"🇸🇾 المبلغ بالليرة: {amount_syp:,.0f} ل.س\n"
                        f"💵 المبلغ بالدولار: ${amount_usd:.2f}\n"
                        f"💱 سعر الصرف: {exchange_rate}\n\n"
                        f"📩 أرسل رقم العملية (رقم التحويل):"
                    )
                    return
                except:
                    await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                    return
            
            if "amount" not in d:
                try:
                    amount = float(text)
                    if amount <= 0:
                        await update.message.reply_text("⚠️ يجب أن يكون المبلغ أكبر من 0")
                        return
                    d["amount"] = amount
                    await update.message.reply_text(f"💰 المبلغ: ${amount:.2f}\n\n📩 أرسل رقم العملية (رقم التحويل):")
                    return
                except:
                    await update.message.reply_text("⚠️ الرجاء إدخال رقم صحيح")
                    return
            
            elif "transaction_number" not in d:
                transaction_number = text
                d["transaction_number"] = transaction_number
                
                payment_method = d["payment_method"]
                amount = d["amount"]
                is_syp = d.get("is_syp", False)
                amount_syp = d.get("amount_syp", 0)
                exchange_rate = d.get("exchange_rate", 1)
                
                cur.execute(
                    "INSERT INTO balance_requests (user_id, username, amount, payment_method, transaction_number) VALUES (?, ?, ?, ?, ?)", 
                    (user.id, user.username, amount, payment_method, transaction_number)
                )
                conn.commit()
                request_id = cur.lastrowid
                
                syp_text = f"\n🇸🇾 المبلغ بالليرة: {amount_syp:,.0f} ل.س\n💱 سعر الصرف: {exchange_rate}" if is_syp else ""
                
                caption = (
                    f"💰 طلب إضافة رصيد جديد\n"
                    f"{'─' * 30}\n"
                    f"🆔 معرف المستخدم: `{user.id}`\n"
                    f"👤 اسم المستخدم: @{user.username or 'لا يوجد'}\n"
                    f"💳 طريقة الدفع: {payment_method}\n"
                    f"💵 المبلغ بالدولار: ${amount:.2f}{syp_text}\n"
                    f"🔢 رقم العملية: {transaction_number}\n"
                    f"🆔 رقم الطلب: #{request_id}\n"
                    f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ قبول", callback_data=f"accept_balance_{request_id}"),
                     InlineKeyboardButton("❌ رفض", callback_data=f"reject_balance_{request_id}")]
                ])
                
                sent_message = await context.bot.send_message(BALANCE_CHANNEL, caption, reply_markup=keyboard)
                cur.execute("UPDATE balance_requests SET channel_msg_id = ? WHERE id = ?", (sent_message.message_id, request_id))
                conn.commit()
                
                await update.message.reply_text(
                    f"✅ تم إرسال طلب إضافة الرصيد بنجاح!\n\n"
                    f"💰 المبلغ: ${amount:.2f}\n"
                    f"🔢 رقم العملية: {transaction_number}\n\n"
                    f"سيتم مراجعة طلبك من قبل الإدارة"
                )
                del user_data[user_id]
                return

    except Exception as e:
        print(f"Error in universal_handler: {e}")

async def send_accounts(update: Update, rows):
    if not rows:
        await update.message.reply_text("❌ لا توجد حسابات")
        return
    
    for row in rows:
        acc_id = row[0]
        level = row[1]
        likes = row[2]
        prime = row[3]
        evo = row[4]
        dances = row[5]
        link_type = row[6]
        recovery = row[7]
        price = row[8]
        acc_type = row[9]
        images = row[10]
        
        caption = (
            f"🎮 حساب #{acc_id}\n{'─' * 30}\n"
            f"📊 • اللفل: {level}\n❤️ • اللايكات: {likes}\n"
            f"👑 • البرايم: {prime}\n⚔️ • الإيفو: {evo}\n"
            f"💃 • الرقصات: {dances}\n🔗 • الربط: {link_type}\n"
            f"♻️ • استعادة: {recovery}\n📦 • النوع: {acc_type}\n"
            f"💰 • السعر: {price}$"
        )
        
        images_list = images.split(",")
        media = []
        for i, img in enumerate(images_list):
            if i == 0:
                media.append(InputMediaPhoto(media=img, caption=caption))
            else:
                media.append(InputMediaPhoto(media=img))
        
        await update.message.reply_media_group(media=media)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 شراء", callback_data=f"buy_{acc_id}"),
             InlineKeyboardButton("📌 حجز", callback_data=f"reserve_{acc_id}")]
        ])
        await update.message.reply_text(f"اختر العملية للحساب #{acc_id}", reply_markup=keyboard)

# ================= PHOTO HANDLER =================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        user_id = user.id
        
        if user_id in admin_data and admin_data[user_id].get("step") == "images":
            d = admin_data[user_id]
            d["images"].append(update.message.photo[-1].file_id)
            if len(d["images"]) == 3:
                d["step"] = "account_info"
                await update.message.reply_text(
                    "📝 أدخل معلومات الحساب:\n\n"
                    "📧 الإيميل:\n🔑 كلمة السر:\n📌 أي معلومات إضافية:\n\n"
                    "اكتبها كلها برسالة واحدة"
                )
            else:
                await update.message.reply_text(f"📸 أرسل الصورة {len(d['images']) + 1}/3")
            return
    except Exception as e:
        print(f"Error in handle_photo: {e}")

# ================= CALLBACK HANDLERS =================
async def confirm_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        
        if user_id not in admin_data:
            await query.message.edit_text("❌ لا توجد بيانات")
            return
        
        if query.data == "no":
            del admin_data[user_id]
            await query.message.edit_text("❌ تم الإلغاء")
            return
        
        d = admin_data[user_id]
        d["step"] = "account_info"
        await query.message.edit_text("📝 أدخل معلومات الحساب (بريد + باسورد):")
    except Exception as e:
        print(f"Error in confirm_account: {e}")

async def buy_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        data = query.data
        user = query.from_user
        
        if data.startswith("confirm_buy_"):
            acc_id = data.split("_")[2]
            cur.execute("SELECT price, channel_msg_ids, acc_type, level, account_info FROM accounts WHERE id = ?", (acc_id,))
            result = cur.fetchone()
            if not result:
                await query.message.edit_text("❌ الحساب غير موجود أو تم بيعه")
                return
            
            price, channel_msg_ids, acc_type, level, account_info = result
            cur.execute("SELECT balance, total_spent FROM users WHERE user_id = ?", (user.id,))
            user_data_result = cur.fetchone()
            if not user_data_result or user_data_result[0] < price:
                await query.message.edit_text("❌ رصيدك غير كافي!")
                return
            
            new_balance = user_data_result[0] - price
            new_total_spent = user_data_result[1] + price
            cur.execute("UPDATE users SET balance = ?, total_spent = ? WHERE user_id = ?", (new_balance, new_total_spent, user.id))
            cur.execute("INSERT INTO orders (acc_id, user_id, username, status, price, paid_amount) VALUES (?, ?, ?, ?, ?, ?)", (acc_id, user.id, user.username, "pending_delivery", price, price))
            order_id = cur.lastrowid
            
            await delete_channel_messages(context, channel_msg_ids)
            cur.execute("DELETE FROM accounts WHERE id = ?", (acc_id,))
            conn.commit()
            
            try:
                admin_msg = await context.bot.send_message(ADMIN_CHANNEL,
                    f"🛒 عملية بيع جديدة\n{'─' * 30}\n🎮 رقم الحساب: #{acc_id}\n📦 النوع: {acc_type}\n📊 المستوى: {level}\n💰 السعر: ${price:.2f}\n\n👤 المشتري:\n• الاسم: @{user.username or 'بدون يوزر'}\n• المعرف: `{user.id}`\n\n📝 معلومات الحساب:\n{account_info or 'لا توجد معلومات مسبقة'}\n\n⚠️ اضغط الزر أدناه لإرسال المعلومات للمشتري",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📩 تسليم للمشتري", callback_data=f"deliver_{order_id}"), InlineKeyboardButton("✅ تم التسليم يدوياً", callback_data=f"delivered_{order_id}")]]))
                cur.execute("UPDATE orders SET admin_msg_id = ? WHERE id = ?", (admin_msg.message_id, order_id))
                conn.commit()
            except:
                pass
            
            await query.message.edit_text(f"✅ تم شراء الحساب #{acc_id} بنجاح!\n\n📦 النوع: {acc_type}\n📊 المستوى: {level}\n💰 تم خصم: ${price:.2f}\n💳 رصيدك المتبقي: ${new_balance:.2f}\n\n📩 سيتم إرسال معلومات الحساب لك قريباً\n💬 إذا تأخر الإرسال، تواصل مع: @AXS_Admin")
            try:
                await context.bot.send_message(user.id, f"🎉 مبروك! تم شراء الحساب #{acc_id}\n\n📩 جاري تجهيز معلومات الحساب...\nسيتم إرسالها لك هنا في هذه المحادثة قريباً\n\n💬 للاستفسار: @AXS_Admin")
            except:
                pass
            return
        
        if data.startswith("buy_"):
            acc_id = data.split("_")[1]
            cur.execute("SELECT price, acc_type, level FROM accounts WHERE id = ?", (acc_id,))
            result = cur.fetchone()
            if not result:
                await query.message.edit_text("❌ الحساب غير موجود")
                return
            price, acc_type, level = result
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✅ نعم، متأكد من الشراء", callback_data=f"confirm_buy_{acc_id}"), InlineKeyboardButton("❌ إلغاء", callback_data=f"cancel_buy_{acc_id}")]])
            await query.message.edit_text(f"⚠️ تأكيد شراء الحساب #{acc_id}\n\n📦 النوع: {acc_type}\n📊 المستوى: {level}\n💰 السعر: ${price:.2f}\n\nهل أنت متأكد من عملية الشراء؟", reply_markup=keyboard)
            return
        
        if data.startswith("cancel_buy_"):
            acc_id = data.split("_")[2]
            await query.message.edit_text(f"❌ تم إلغاء شراء الحساب #{acc_id}")
            return
    except Exception as e:
        print(f"Error in buy_account: {e}")

async def handle_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        data = query.data
        user = query.from_user
        
        if not user or user.id not in ADMIN_ID:
            await query.answer("❌ غير مصرح لك", show_alert=True)
            return
        
        if data.startswith("deliver_"):
            order_id = int(data.split("_")[1])
            cur.execute("SELECT * FROM orders WHERE id = ? AND status = 'pending_delivery'", (order_id,))
            order = cur.fetchone()
            if not order:
                await query.answer("❌ الطلب غير موجود أو تم تسليمه مسبقاً", show_alert=True)
                return
            
            admin_data[user.id] = {"step": "deliver_info", "order_id": order_id, "buyer_id": order[2], "acc_id": order[1], "price": order[6], "admin_msg_id": order[9]}
            await context.bot.send_message(chat_id=user.id, text="📝 أدخل معلومات الحساب لتسليمها للمشتري:\n\nاكتب المعلومات بالصيغة التالية:\n📧 البريد: ...\n🔑 كلمة السر: ...\n📌 ملاحظات: ...\n\nسيتم إرسالها مباشرة للمشتري")
            return
        
        if data.startswith("delivered_"):
            order_id = int(data.split("_")[1])
            cur.execute("UPDATE orders SET status = 'completed' WHERE id = ? AND status = 'pending_delivery'", (order_id,))
            conn.commit()
            try:
                await query.message.delete()
            except:
                pass
            await query.answer("✅ تم التأكيد", show_alert=True)
            return
    except Exception as e:
        print(f"Error in handle_delivery: {e}")

async def reserve_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        data = query.data
        user = query.from_user
        user_id = user.id
        
        if data.startswith("confirm_reserve_"):
            acc_id = data.split("_")[2]
            cur.execute("SELECT * FROM accounts WHERE id = ?", (acc_id,))
            acc = cur.fetchone()
            if not acc:
                await query.message.edit_text("❌ الحساب غير موجود أو تم بيعه")
                return
            
            price = acc[8]
            reserve_fee = round(price * 0.05, 2)
            channel_msg_ids = acc[11] if len(acc) > 11 else None
            
            cur.execute("SELECT balance, total_spent FROM users WHERE user_id = ?", (user_id,))
            user_data_result = cur.fetchone()
            if not user_data_result or user_data_result[0] < reserve_fee:
                await query.message.edit_text(f"❌ رصيدك لا يكفي\nالمطلوب: ${reserve_fee:.2f}")
                return
            
            new_balance = user_data_result[0] - reserve_fee
            new_total_spent = user_data_result[1] + reserve_fee
            cur.execute("UPDATE users SET balance = ?, total_spent = ? WHERE user_id = ?", (new_balance, new_total_spent, user_id))
            
            account_data = {"level": acc[1], "likes": acc[2], "prime": acc[3], "evo": acc[4], "dances": acc[5], "link_type": acc[6], "recovery": acc[7], "price": price, "acc_type": acc[9], "images": acc[10], "channel_msg_ids": channel_msg_ids, "account_info": acc[12] if len(acc) > 12 else None}
            cur.execute("INSERT INTO orders (acc_id, user_id, username, status, price, paid_amount, account_data) VALUES (?, ?, ?, ?, ?, ?, ?)", (acc_id, user_id, user.username, "reserved", price, reserve_fee, json.dumps(account_data)))
            
            if channel_msg_ids:
                await delete_channel_messages(context, channel_msg_ids)
            
            cur.execute("DELETE FROM accounts WHERE id = ?", (acc_id,))
            conn.commit()
            
            await query.message.edit_text(
                f"✅ تم حجز الحساب #{acc_id}\n\n📦 النوع: {acc[9]}\n📊 المستوى: {acc[1]}\n💰 تم خصم: ${reserve_fee:.2f} (5%)\n💳 رصيدك المتبقي: ${new_balance:.2f}\n📌 المبلغ المتبقي: ${price - reserve_fee:.2f}\n\n⚠️ تنبيه: إذا ألغيت الحجز، لن تسترد مبلغ الخصم\nعند إكمال المبلغ سنقوم بتسليم الحساب تلقائياً",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💳 شراء الحساب", callback_data=f"reserved_buy_{acc_id}"), InlineKeyboardButton("❌ إلغاء الحجز", callback_data=f"reserved_cancel_{acc_id}")]]))
            return
        
        if data.startswith("reserved_buy_"):
            acc_id = data.split("_")[2]
            cur.execute("SELECT * FROM orders WHERE acc_id = ? AND user_id = ? AND status = 'reserved'", (acc_id, user_id))
            order = cur.fetchone()
            if not order:
                await query.message.edit_text("❌ لا يوجد حجز لهذا الحساب")
                return
            
            full_price = order[6]
            paid_amount = order[7] or 0
            remaining = round(full_price - paid_amount, 2)
            
            cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            user_balance = cur.fetchone()
            
            if not user_balance or user_balance[0] < remaining:
                await query.answer(f"❌ رصيدك غير كافٍ!\n\n💰 المطلوب: ${remaining:.2f}\n💳 رصيدك الحالي: ${user_balance[0]:.2f}", show_alert=True)
                return
            
            new_balance = user_balance[0] - remaining
            cur.execute("UPDATE users SET balance = ?, total_spent = total_spent + ? WHERE user_id = ?", (new_balance, remaining, user_id))
            
            account_data = json.loads(order[8])
            account_info = account_data.get("account_info", "لا توجد معلومات")
            
            cur.execute("UPDATE orders SET status = 'pending_delivery', paid_amount = ? WHERE id = ?", (full_price, order[0]))
            conn.commit()
            
            try:
                admin_msg = await context.bot.send_message(ADMIN_CHANNEL,
                    f"🛒 إكمال حجز - عملية بيع\n{'─' * 30}\n🎮 رقم الحساب: #{acc_id}\n📦 النوع: {account_data.get('acc_type', 'غير معروف')}\n📊 المستوى: {account_data.get('level', 'غير معروف')}\n💰 السعر الكامل: ${full_price:.2f}\n💳 المدفوع سابقاً: ${paid_amount:.2f}\n💳 المدفوع الآن: ${remaining:.2f}\n\n👤 المشتري:\n• الاسم: @{user.username or 'بدون يوزر'}\n• المعرف: `{user.id}`\n\n📝 معلومات الحساب:\n{account_info}\n\n⚠️ اضغط الزر أدناه لإرسال المعلومات للمشتري",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📩 تسليم للمشتري", callback_data=f"deliver_{order[0]}"), InlineKeyboardButton("✅ تم التسليم يدوياً", callback_data=f"delivered_{order[0]}")]]))
                cur.execute("UPDATE orders SET admin_msg_id = ? WHERE id = ?", (admin_msg.message_id, order[0]))
                conn.commit()
            except:
                pass
            
            await query.message.edit_text(f"✅ تم شراء الحساب #{acc_id} بنجاح!\n\n💰 تم خصم: ${remaining:.2f}\n💳 رصيدك المتبقي: ${new_balance:.2f}\n\n📩 سيتم إرسال معلومات الحساب هنا قريباً\nشكراً لتفهمكم 💚")
            try:
                await context.bot.send_message(user.id, f"🎉 مبروك! تم إكمال شراء الحساب #{acc_id}\n\n📩 جاري تجهيز معلومات الحساب...\n\n💬 للاستفسار: @AXS_Admin")
            except:
                pass
            return
        
        if data.startswith("reserved_cancel_"):
            acc_id = data.split("_")[2]
            cur.execute("SELECT * FROM orders WHERE acc_id = ? AND user_id = ? AND status = 'reserved'", (acc_id, user_id))
            order = cur.fetchone()
            if not order:
                await query.message.edit_text("❌ لا يوجد حجز لهذا الحساب")
                return
            
            account_data_str = order[8]
            if not account_data_str:
                await query.message.edit_text("❌ لا توجد بيانات للحساب")
                return
            
            account_data = json.loads(account_data_str)
            cur.execute("INSERT INTO accounts (level, likes, prime, evo, dances, link_type, recovery, price, acc_type, images, channel_msg_ids, account_info) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (account_data["level"], account_data["likes"], account_data["prime"], account_data["evo"], account_data["dances"], account_data["link_type"], account_data["recovery"], account_data["price"], account_data["acc_type"], account_data["images"], "", account_data.get("account_info", "")))
            new_acc_id = cur.lastrowid
            await restore_account_to_channel(context, account_data, new_acc_id)
            cur.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", (order[0],))
            conn.commit()
            paid_amount = order[7] or 0
            await query.message.edit_text(f"❌ تم إلغاء الحجز\n\nالحساب عاد للقناة برقم #{new_acc_id}\n💰 لم يتم استرداد مبلغ ${paid_amount:.2f}\n\nيمكنك شراء الحساب مرة أخرى من القناة")
            return
        
        if data.startswith("reserve_"):
            acc_id = data.split("_")[1]
            cur.execute("SELECT price, acc_type, level FROM accounts WHERE id = ?", (acc_id,))
            result = cur.fetchone()
            if not result:
                await query.message.edit_text("❌ الحساب غير موجود")
                return
            price, acc_type, level = result
            fee = round(price * 0.05, 2)
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✅ نعم، احجز بـ 5%", callback_data=f"confirm_reserve_{acc_id}"), InlineKeyboardButton("❌ إلغاء", callback_data=f"cancel_reserve_{acc_id}")]])
            await query.message.edit_text(f"⚠️ تأكيد حجز الحساب #{acc_id}\n\n📦 النوع: {acc_type}\n📊 المستوى: {level}\n💰 السعر الكامل: ${price:.2f}\n📌 مبلغ الحجز (5%): ${fee:.2f}\n\n⚠️ تنبيه مهم: إذا ألغيت الحجز لاحقاً، لن يتم استرداد مبلغ الخصم", reply_markup=keyboard)
            return
        
        if data.startswith("cancel_reserve_"):
            acc_id = data.split("_")[2]
            await query.message.edit_text(f"❌ تم إلغاء حجز الحساب #{acc_id}")
            return
    except Exception as e:
        print(f"Error in reserve_account: {e}")

async def accept_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        if query.from_user.id not in ADMIN_ID:
            return
        
        request_id = int(query.data.split("_")[2])
        cur.execute("SELECT user_id, amount, transaction_number, channel_msg_id, date FROM balance_requests WHERE id = ? AND status = 'pending'", (request_id,))
        result = cur.fetchone()
        
        if not result:
            await query.message.edit_text("❌ الطلب غير موجود أو تمت معالجته")
            return
        
        user_id, amount, transaction_number, channel_msg_id, request_date = result
        time_str = calculate_time_difference(request_date)
        processed_time = datetime.now()
        
        cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        cur.execute("UPDATE balance_requests SET status = 'approved', processed_date = ? WHERE id = ?", (processed_time, request_id))
        conn.commit()
        
        cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        new_balance = cur.fetchone()[0]
        
        if channel_msg_id:
            try:
                caption = f"💰 طلب إضافة رصيد - ✅ تم القبول\n{'─' * 30}\n🆔 معرف المستخدم: `{user_id}`\n💰 المبلغ: ${amount:.2f}\n🔢 رقم العملية: {transaction_number or 'لا يوجد'}\n🆔 رقم الطلب: #{request_id}\n📅 تاريخ الطلب: {request_date[:16]}\n✅ تاريخ القبول: {processed_time.strftime('%Y-%m-%d %H:%M')}\n⏱ الوقت المستغرق: {time_str}\n📌 الحالة: تم القبول ✅"
                await context.bot.edit_message_text(chat_id=BALANCE_CHANNEL, message_id=channel_msg_id, text=caption)
            except:
                pass
        
        await context.bot.send_message(user_id, f"✅ تم قبول طلب إضافة الرصيد\n{'─' * 30}\n💰 المبلغ: ${amount:.2f}\n🔢 رقم العملية: {transaction_number or 'لا يوجد'}\n💳 الرصيد الكلي: ${new_balance:.2f}\n⏱ وقت المعالجة: {time_str}\n\nشكراً على استخدام المتجر الخاص بنا 🌹")
        await query.message.edit_text(f"✅ تم قبول الطلب #{request_id}")
    except Exception as e:
        print(f"Error in accept_balance: {e}")

async def reject_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        if query.from_user.id not in ADMIN_ID:
            return
        
        request_id = int(query.data.split("_")[2])
        cur.execute("SELECT user_id, amount, transaction_number, channel_msg_id, date FROM balance_requests WHERE id = ? AND status = 'pending'", (request_id,))
        result = cur.fetchone()
        
        if not result:
            await query.message.edit_text("❌ الطلب غير موجود أو تمت معالجته")
            return
        
        user_id, amount, transaction_number, channel_msg_id, request_date = result
        time_str = calculate_time_difference(request_date)
        processed_time = datetime.now()
        
        cur.execute("UPDATE balance_requests SET status = 'rejected', processed_date = ? WHERE id = ?", (processed_time, request_id))
        conn.commit()
        
        if channel_msg_id:
            try:
                caption = f"💰 طلب إضافة رصيد - ❌ تم الرفض\n{'─' * 30}\n🆔 معرف المستخدم: `{user_id}`\n💰 المبلغ: ${amount:.2f}\n🔢 رقم العملية: {transaction_number or 'لا يوجد'}\n🆔 رقم الطلب: #{request_id}\n📅 تاريخ الطلب: {request_date[:16]}\n❌ تاريخ الرفض: {processed_time.strftime('%Y-%m-%d %H:%M')}\n⏱ الوقت المستغرق: {time_str}\n📌 الحالة: تم الرفض ❌"
                await context.bot.edit_message_text(chat_id=BALANCE_CHANNEL, message_id=channel_msg_id, text=caption)
            except:
                pass
        
        await context.bot.send_message(user_id, f"❌ تم رفض طلب إضافة الرصيد\n{'─' * 30}\n💰 المبلغ: ${amount:.2f}\n🔢 رقم العملية: {transaction_number or 'لا يوجد'}\n⏱ وقت المعالجة: {time_str}\n\nنعتذر عن عدم قبول الرصيد\nالرجاء التواصل مع الدعم: @AXS_Admin")
        await query.message.edit_text(f"❌ تم رفض الطلب #{request_id}")
    except Exception as e:
        print(f"Error in reject_balance: {e}")

# ================= APP =================
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_sub$"))
app.add_handler(CallbackQueryHandler(categories_callback, pattern="^show_categories$|^cat_|^buy_product_|^confirm_product_|^cancel_product_|^approve_product_|^reject_product_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, universal_handler))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

app.add_handler(CallbackQueryHandler(confirm_account, pattern="^(yes|no)$"))
app.add_handler(CallbackQueryHandler(buy_account, pattern="^buy_|^confirm_buy_|^cancel_buy_"))
app.add_handler(CallbackQueryHandler(handle_delivery, pattern="^deliver_|^delivered_"))
app.add_handler(CallbackQueryHandler(reserve_account, pattern="^reserve_|^confirm_reserve_|^cancel_reserve_|^reserved_buy_|^reserved_cancel_"))
app.add_handler(CallbackQueryHandler(accept_balance, pattern="^accept_balance_"))
app.add_handler(CallbackQueryHandler(reject_balance, pattern="^reject_balance_"))

print("🚀 Bot is running...")
app.run_polling()

