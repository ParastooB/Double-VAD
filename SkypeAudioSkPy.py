from skpy import Skype
username = "parastoouw@gmail.com"
password = "**************"
sk = Skype(username, password) # connect to Skype

sk.user # you
sk.contacts # your contacts
sk.chats # your conversations

print(sk.user)
print(sk.contacts)
print(sk.chats)

# ch = sk.chats.create(["parastoo.baghaei"]) # new group conversation
ch3 = ch = sk.contacts
ch = sk.contacts["parastoo.baghaei"].chat # 1-to-1 conversation

# ch.sendMsg("hello") # plain-text message
# ch.sendFile(open("vad_org.py", "rb"), "vad_org.py") # file upload
# ch.sendContact(sk.contacts["daisy.5"]) # contact sharing

ch.getMsgs() # retrieve recent messages

ch2 = sk.contacts["parastoo.baghaei"]
print(ch2.birthday)
print(ch3.user("parastoo.baghaei"))