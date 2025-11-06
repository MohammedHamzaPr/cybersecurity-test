from telebot import TeleBot, types
import os, json, time

bot = TeleBot('8354437515:AAHdlQ7qzbfI0rNk_C_8ukZBw4fM20nQ0kk')

if not os.path.exists('users.json'):
    with open('users.json', 'w', encoding='utf-8') as file:
        json.dump({}, file, ensure_ascii=False, indent=4)

def load_users():
    with open('users.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def save_users(data):
    with open('users.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

users = load_users()
admins = json.loads(open('admins.json', 'r', encoding='utf-8').read())
qu = json.loads(open('q.json', 'r', encoding='utf-8').read())


def send_notification(message):
    for i in admins:
        try:
            bot.send_message(i, message)
        except:pass

def the_test(answer, user_id, q_n, message_id):
    if answer == 'الغاء':
        bot.send_message(user_id, 'تم الغاء الأختبار')
    else:
        bot.delete_messages(user_id,[message_id,message_id+1])
        global users
        users = load_users()
        if q_n == 0:
            if users[user_id]['attempts'] != 3:
                ms = 'حسناً يبدو لي انك مستعد هيا لنبدء ولكن لاحظ ان هذه ليست محاولتك الأولى لذلك ركز هذه عدد المحاولات الباقية ' + str(int(users[user_id]['attempts']) - 1)
                t = 5
            else:
                ms = 'حسنا يبدو لي انك مستعد وهذه محاولتك الأولى بالتوفيق يا صديقي'
                t = 3
            bot.edit_message_text(ms,user_id, message_id-1)
            time.sleep(t)
            bot.edit_message_text('لقد بداء الأختبار',user_id, message_id-1)

            users[user_id]['answers'] = 0
            users[user_id]['attempts'] -= 1
            save_users(users)
        else:
            if answer.upper() == qu[str(q_n)]['Current']:
                users = load_users()
                users[user_id]['answers'] += 1
                save_users(users)

        try:
            message = qu[str(q_n+1)]['q'] + ''.join(i for i in qu[str(q_n+1)]['options'])
            q = bot.send_message(user_id, message)
            bot.register_next_step_handler(q, lambda e: the_test(e.text, user_id, q_n+1, q.message_id))
        except:
            if users[user_id]['answers'] < 3:
                bot.send_message(user_id, 'حسناً يبدو لي اانك انهيت الأجوبة ولكنك مع الأسف راسب')
            else:
                bot.send_message(user_id, 'حسناً يبدو لي اانك انهيت الأجوبة جميعها ونتيجتك ناجح مبارك لك')
                        
                send_notification(f"""اكلك اكو طالب نجح بالأختبار وهاي المعلومات كاملة
الأسم الكامل: {users[user_id]['full name']}
رقم التليفون مالته: {users[user_id]['phone number']}
أيدي حسابة: {user_id}
يوزر حسابة: {users[user_id]['username']}
عدد المحاولات الباقية: {users[user_id]['attempts']}
عدد الأجوبة الصحيحة: {users[user_id]['answers']} من اصل 37""")


def reset_attempts(e):
    users[e.text]['attempts'] = 3
    save_users(users)
    bot.send_message(e.from_user.id, 'تم اعادة تعين عدد المحاولات الى 3')
    bot.send_message(e.text,'تم اعادة عدد المحاولات لديك الى 3')




def share_number():
	buttons = types.ReplyKeyboardMarkup(True,row_width=2)
	button = types.KeyboardButton(
text='انا لست برنامج روبوت',
request_contact=True
)
	buttons.add(button)
	return buttons


def add_new_user(message, number):
    if len(message.text.split(' ')) == 3:
        users[message.from_user.id] = {"attempts": 3,
                                    "answers": 0,
                                    "full name":message.text,
                                    "username":message.from_user.username,
                                    "phone number":number.phone_number}
        save_users(users)
        bot.send_message(message.from_user.id,'تم أضافتك بنجاح لبداء الأختبار ارسل /start مرة اخرى')
        send_notification(f'''دخل شخص لبوت وهاذي معلوماته
الأسم الكامل: {message.text}
اليوزر: {message.from_user.username}
رقم التليفون: {number.phone_number}
ايدي حسابة: {message.from_user.id}''')
    else:
        bot.send_message(message.from_user.id, 'تم رفض المعلومات بسبب الأسم الرجأ اعادة المحاولة مرة اخرى او التواصل مع المسؤول\n@lw_w7 @dk_d4')

@bot.message_handler(commands=['json'])
def json_send(m):
    bot.send_document(m.from_user.id,open('users.json','r',encoding='utf-8'),caption='هذا ملف المستخدمين')


@bot.message_handler(content_types='contact')
def contact(num):
    if num.contact.user_id == num.from_user.id:
        m = bot.send_message(num.from_user.id, 'الرجأ ارسال اسمك الثلاثي من اجل بدء الأختبار\nملاحظة اذا كان اسمك مركب مثل عبد الرحمن يجب كتابة بهذا الشكل: عبدالرحمن من غير مسافة وفي حال لم يكن كذلك سوف يتم استبعادك من الأختبار', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(m, lambda e:add_new_user(e, num.contact))
    else:
        bot.reply_to(num, 'الرجأ الضغط على زر انا لست برنامج روبوت')

@bot.message_handler(commands=['run'])
def send_run(self):
    send_notification('مرحبا استاذ انا مستعد للعمل مرة اخرة')

@bot.message_handler(commands=['start'])
def start(call):
    if not os.path.exists('users.json'):
        with open('users.json', 'w', encoding='utf-8') as file:
            json.dump({}, file, ensure_ascii=False, indent=4)
    user_id = str(call.from_user.id)
    users = load_users()
    if user_id not in users:
        bot.send_message(
            user_id,
            text='الرجأ الضغط على زر انا لست برنامج روبوت',
            parse_mode='markdown'
        )
        bot.reply_to(
            call,
            text='انا لست برنامج روبوت',
            reply_markup=share_number()
        )
    elif int(users[user_id]['attempts']) == 0:
        bot.send_message(user_id, f'عفواً ولكن عدد محاولاتك قد نفذ الرجأ التواصل مع الأدارة من اجل حل المشكلة\nمحمد حمزة: @lw_w7\nابراهيم عباس: @dk_d4\nهذا الأيدي الخاص بك: {user_id}')
    else:
        message = bot.send_message(call.from_user.id, '''مرحبا بيك ببوت الأختبارات
تم برمجة هذا البوت من قبل المهندس محمد حمزة: @lw_w7
تم اعداد هذا البوت من قبل المهندس ابراهيم عباس : @dk_d4

هذا البوت سوف يختبرك بعدة اسئلة وانت يجب عليك اختيار الجواب الصحيح سوف يكون طريقة الأختبار كالأتي

سؤال الأختبار
A. الجواب الأول
B. الجواب الثاني
C. الجواب الثالث
يجب عليك ارسل الحرف الخاص بالجواب مثلا A او a لا فرق وبعدها مباشرة سوف يتم طرح عليك السؤال التالي وطريقة الأجابة بنفس الطريقة ونتمنى لكم النجاح في الأختبار

ولأيقاف الأختبار ارسل كلمة الغاء ولكن لاحظ انك في حالة بدأت الأختبار وقمت بالألغاء اثناء الأختبار سوف تذهب احد فرصك
                                   

والأن ارسل أي شيء من اجل التأكد انك قرأت الرسالة كاملة او ارسل الغاء لألغاء الأختبار بدون فقدان محاولتك''')
        bot.register_next_step_handler(message, lambda e: the_test(e.text, user_id, 0, e.message_id))


@bot.message_handler(commands=['reset'])
def reset(e):
    if str(e.from_user.id) not in admins:
        bot.send_message(e.from_user.id, 'حبيبي انت مو ادمن طير')
    else:
        m = bot.send_message(e.from_user.id, 'دز ايدي العضو')
        bot.register_next_step_handler(m, reset_attempts)

bot.infinity_polling(skip_pending=True)
