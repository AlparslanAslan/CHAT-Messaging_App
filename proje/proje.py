import socket
import threading
import queue
import time
class loggerThread(threading.Thread):
    def __init__(self,loggerQueue,conn,addr):
        threading.Thread.__init__(self)
        self.loggerQueue = loggerQueue
        self.conn = conn
        self.addr = addr
        def run(self):
            logger(self.loggerQueue)
def logger(loggerQueue):
    info = loggerQueue.get()
    print(info.encode())
class writeThread(threading.Thread):
    def __init__(self,threadID,conn,addr,workQueue):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.conn = conn
        self.addr = addr
        self.workQueue = workQueue
    def run(self):
        while True:
            request = self.workQueue.get()
            self.conn.send(request.encode())   
        self.conn.close()
        
        
class readThread(threading.Thread):
    def __init__(self,threadID,conn,addr,clientDict,pidDict,workQueue,roomDict):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.conn = conn
        self.addr = addr
        self.clientDict = clientDict
        self.pidDict = pidDict
        self.workQueue = workQueue
        self.roomDict= roomDict
    def run(self):
        parser(self.threadID,self.clientDict,self.pidDict,self.workQueue,self.conn,self.roomDict)
        
def parser(threadID,clientDict,pidDict,workQueue,conn,roomDict):
    while True:
            data = conn.recv(1024)
            dataStr = data.decode().strip().split(":")
            message = dataStr[0].split(" ")
            if message[0] == "REG":
                if len(message) == 3:
                    req = ""
                    number =len(clientDict)
                    if number > 0:
                        if message[1] in clientDict:
                            if threadID in pidDict and pidDict[threadID] == message[1]:
                                if clientDict[message[1]][3] == True:
                                
                                    if len(message[2]) == 4:
                                        try:
                                            sifre = int(message[2])
                                            req += "OKS (sifre guncellendi)\n"
                                            clientDict[message[1]][0] = message[2]
                                            #print(clientDict)
                                            queueLock.acquire()
                                            workQueue.put(req)
                                            queueLock.release()
                                        
                
                                        except:
                                            req += "REJN(sifre sadece sayilardan olusmalidir)\n"
                                            queueLock.acquire()
                                            workQueue.put(req)
                                            queueLock.release()
                                    else:
                                        req += "REJN (sifre 4 rakamdan olusmalidir)\n"
                                        queueLock.acquire()
                                        workQueue.put(req)
                                        queueLock.release()
                                
                                else:
                                    req += "REJN (baska isim kullan)\n"
                                    queueLock.acquire()
                                    workQueue.put(req)
                                    queueLock.release()
                            else:
                                req += "REJN (baska isim kullan)\n"
                                queueLock.acquire()
                                workQueue.put(req)
                                queueLock.release()
                        #---------------------------------------
                        else:
                            if len(message[2]) == 4:
                                try:
                                    sifre = int(message[2])
                                    req += "WELN (kayıt olundu)"+message[1] + "\n"
                                    clientDict[message[1]] = [1,2,[],False]
                                    clientDict[message[1]][0] = message[2]
                                    clientDict[message[1]][1] = workQueue
                                    pidDict[threadID] = message[1]
                                    #print(clientDict)
                                    queueLock.acquire()
                                    workQueue.put(req)
                                    queueLock.release()
                                
                
                                except:
                                    req += "REJN(sifre sadece sayilardan olusmalidir)\n"
                                    queueLock.acquire()
                                    workQueue.put(req)
                                    queueLock.release()
                            else:
                                req += "REJN (sifre 4 rakamdan olusmalidir)\n"
                                queueLock.acquire()
                                workQueue.put(req)
                                queueLock.release()
                #-----------------------------------------------------------------
                    else:
                        if len(message[2]) == 4:
                            try:
                                sifre = int(message[2])
                                req += "WELN (kayıt olundu) "+message[1] + "\n"
                                clientDict[message[1]] = [1,2,[],False]
                                clientDict[message[1]][0] = message[2]
                                clientDict[message[1]][1] = workQueue
                                pidDict[threadID] = message[1]
                                #print(clientDict)
                                queueLock.acquire()
                                workQueue.put(req)
                                queueLock.release()
                
                            except:
                                req += "REJN(sifre sadece sayilardan olusmalidir)\n"
                                queueLock.acquire()
                                workQueue.put(req)
                                queueLock.release()
                        else:
                            req += "REJN (sifre 4 rakamdan olusmalidir)\n"
                            queueLock.acquire()
                            workQueue.put(req)
                            queueLock.release()
                else:
                    queueLock.acquire()
                    workQueue.put("Arguman eksik ya da fazla\n")
                    queueLock.release()
                    
                
            elif message[0] == "NIC":
                if len(message) == 3:
                    req = ""
                    if message[1] in clientDict:
                        if message[2] == clientDict[message[1]][0]:
                            req += "WEL (giris yapildi)" + message[1] + "\n"
                            clientDict[message[1]][3] = True
                        else:
                            req += "REJ (sifre hatasi) "+ message[1] + "\n"
                    else:
                        req += "REJ (kullanici yok) " +message[1] + "\n"
                    #print(clientDict)
                    queueLock.acquire()
                    workQueue.put(req)
                    queueLock.release()
                else:
                    queueLock.acquire()
                    workQueue.put("Arguman eksik ya da fazla\n")
                    queueLock.release()
            elif message[0] == "OAC":
                if len(message) == 2:
                    req = ""
                    name = pidDict[threadID]
                    if message[1] in roomDict:
                        req += "REJC " + message[1] + "\n"
                    else:
                        req += "OKC " + message[1] +"\n"
                        roomDict[message[1]] = [[],[],[]]
                        roomDict[message[1]][0].append(pidDict[threadID])
                        clientDict[name][2].append(message[1])
                    
                        print(roomDict)
                    queueLock.acquire()
                    workQueue.put(req)
                    queueLock.release()
                else:
                    queueLock.acquire()
                    workQueue.put("Arguman eksik ya da fazla\n")
                    queueLock.release()
            elif message[0] == "GIR":
                if len(message) == 2:
                    req = ""
                    name = pidDict[threadID]
                    if message[1] in roomDict:
                        if clientDict[name][3] == True:
                            if name in roomDict[message[1]][2]:
                                req += "YSK (Engellenmisin)\n"
                            else:
                                req += "OKO (odaya giris yapildi)\n"
                                bildirim = name +" "+ message[1] + " odasina giris yapti\n"
                                clientDict[name][2].append(message[1])
                                roomDict[message[1]][1].append(name)
                                for i in roomDict[message[1]][1]:
                                    queueLock.acquire()
                                    clientDict[i][1].put(bildirim)
                                    queueLock.release()
                                for j in roomDict[message[1]][0]:
                                    queueLock.acquire()
                                    clientDict[j][1].put(bildirim)
                                    queueLock.release()
                            
                        else:
                            req += "YSK" + "giris yapilmamis\n"
                    else:
                        req += "YSK (oda yok)\n"
                
                    queueLock.acquire()
                    workQueue.put(req)
                    queueLock.release()
                else:
                    queueLock.acquire()
                    workQueue.put("Arguman eksik ya da fazla\n")
                    queueLock.release()
                
            elif message[0] == "QUI":
                name = pidDict[threadID]
                clientDict[name][3] = False
                queueLock.acquire()
                queueList[threadID].put("BYE\n")
                queueLock.release()
            elif message[0] == "PIN":
                queueLock.acquire()
                queueList[threadID].put("PON\n")
                queueLock.release()
            elif message[0] == "PRV":
                if len(message) == 2:
                    name = pidDict[threadID]
                    if name in clientDict:
                        if clientDict[name][3] == True:
                            if message[1] in clientDict:
                                if clientDict[message[1]][3] == True:
                                    if len(dataStr) == 2:
                                        req =pidDict[threadID]  + "->" + dataStr[1] + "\n"
                                        adres = message[1]
                                        queueLock.acquire()
                                        clientDict[adres][1].put(req)
                                        workQueue.put("OKP\n")
                                        queueLock.release()
                                    else:
                                        req = "NOP (mesaj birakmadiniz)\n"
                                        queueLock.acquire()
                                        workQueue.put(req)
                                        queueLock.release()
                                    
                                else:
                                    queueLock.acquire()
                                    workQueue.put("NOP (kullanici online degil)\n")
                                    queueLock.release()
                            else :
                                req = "NOP " + message[1] + "\n"
                                queueLock.acquire()
                                workQueue.put(req)
                                queueLock.release()
                        else:
                            req = "NOP (giris yap) \n"
                            queueLock.acquire()
                            workQueue.put(req)
                            queueLock.release()
                    
                    else:
                        req = "LRR \n"
                        queueLock.acquire()
                        queueList[threadID].put(req)
                        queueLock.release()
                else:
                    queueLock.acquire()
                    workQueue.put("Arguman eksik ya da fazla\n")
                    queueLock.release()
            elif message[0] == "GNL":
                if len(message) == 2:
                    name = pidDict[threadID]
                    if clientDict[name][3] == True:
                        if message[1] in roomDict:
                            if name in roomDict[message[1]][1] or name in roomDict[message[1]][0] :
                                if len(dataStr) == 2:
                                    queueLock.acquire()
                                    workQueue.put("OKG\n")
                                    queueLock.release()
                                    for i in roomDict[message[1]][1]:
                                        req = name + "->" + dataStr[1] + "\n"
                                        queueLock.acquire()
                                        clientDict[i][1].put(req)
                                        queueLock.release()
                                    for j in roomDict[message[1]][0]:
                                        req = name + "->" + dataStr[1] + "\n"
                                        queueLock.acquire()
                                        clientDict[j][1].put(req)
                                        queueLock.release()
                                else:
                                    queueLock.acquire()
                                    workQueue.put("NOG (mesaj birakmadiniz)\n")
                                    queueLock.release()
                            else:
                        
                                queueLock.acquire()
                                workQueue.put("NOG(grupta degilsin)\n")
                                queueLock.release()
                        else:
                            queueLock.acquire()
                            workQueue.put("NOG(oyle oda yok)\n")
                            queueLock.release()
                    #-----------------------
                    else:
                        queueLock.acquire()
                        workQueue.put("NOG(giris yapilmamis)\n")
                        queueLock.release()
                else:
                    queueLock.acquire()
                    workQueue.put("Arguman eksik ya da fazla\n")
                    queueLock.release()
            elif message[0] == "GOL":
                req = ""
                name = pidDict[threadID]
                if len(clientDict[name][2]) > 0:
                    for i in clientDict[name][2]:
                        req += i + ":"
                else:
                    req += "NOK(girilen oda yok)"
                req += "\n"
                queueLock.acquire()
                workQueue.put(req)
                queueLock.release()
                
            elif message[0] == "CIK":
                if len(message) == 2:
                    req = ""
                    name = pidDict[threadID]
                    if message[1] in roomDict:
                        if name in roomDict[message[1]][1]:
                            req += "OKK " + message[1] + "\n"
                            bildirim = name+" "+message[1] +" "+"odasindan cikis yapti\n"
                            roomDict[message[1]][1].remove(name)
                            clientDict[name][2].remove(message[1])
                            for i in roomDict[message[1]][1]:
                                queueLock.acquire()
                                clientDict[i][1].put(bildirim)
                                queueLock.release()
                            for j in roomDict[message[1]][0]:
                                queueLock.acquire()
                                clientDict[j][1].put(bildirim)
                                queueLock.release()   
                        elif name in roomDict[message[1]][0]:
                            req += "OKK " + message[1] + "\n"
                            bildirim = name+" "+message[1] +" "+"odasindan cikis yapti\n"
                            roomDict[message[1]][0].remove(name)
                            clientDict[name][2].remove(message[1])
                            for i in roomDict[message[1]][1]:
                                queueLock.acquire()
                                clientDict[i][1].put(bildirim)
                                queueLock.release()
                            for j in roomDict[message[1]][0]:
                                queueLock.acquire()
                                clientDict[j][1].put(bildirim)
                                queueLock.release()
                        else:
                            req += "NOK (odada degilsin) \n"
                    else:
                        req += "NOK (oda yok) \n"
                    queueLock.acquire()
                    workQueue.put(req)
                    queueLock.release()
                else:
                    queueLock.acquire()
                    workQueue.put("Arguman eksik ya da fazla\n")
                    queueLock.release()
                        
            elif message[0] == "OLS":
                req = "OLST "
                name = pidDict[threadID]
                if clientDict[name][3] == True:
                    for i in roomDict:
                        req += i + ":"
                    req += "\n"
                else:
                    req += "NOLS Giris yapin"
                queueLock.acquire()
                workQueue.put(req)
                queueLock.release()
            elif message[0] == "ENG":
                if len(message) == 3:
                    req = ""
                    name = pidDict[threadID]
                    if clientDict[name][3] == True:
                        if message[1] in roomDict:
                            if name in roomDict[message[1]][0]:
                                req += "OKE\n"
                                bildirim= message[1] + " odasından engellendiniz.\n"
                                roomDict[message[1]][2].append(message[2])
                                queueLock.acquire()
                                clientDict[message[2]][1].put(bildirim)
                                queueLock.release()
                            else:
                                req += "NOE(engel icin yonetici olmak lazim)\n"
                        else:
                            req += "NOE(boyle oda yok)\n"
                    else:
                        req += "NOE(giris yap)\n"
                
                    queueLock.acquire()
                    workQueue.put(req)
                    queueLock.release()
                else:
                    queueLock.acquire()
                    workQueue.put("Arguman eksik ya da fazla\n")
                    queueLock.release()
            elif message[0] == "OKL":
                if len(message) == 2:
                    req = ""
                    name = pidDict[threadID]
                    if clientDict[name][3] == True:
                        if message[1] in roomDict:
                            if message[1] in clientDict[name][2]:
                                for i in roomDict[message[1]][1]:
                                    req += i + ": normal\n"
                                for j in roomDict[message[1]][0]:
                                    req += j + ": yonetici\n"
                            else:
                                req += "NOL(odada yoksun)\n"
                        else:
                            req += "NOL(oyle oda yok)\n"
                    else:
                        req += "NOL(giris yap) \n"
                    queueLock.acquire()
                    workQueue.put(req)
                    queueLock.release()
                else:
                    queueLock.acquire()
                    workQueue.put("Arguman eksik ya da fazla\n")
                    queueLock.release()
            elif message[0] == "KAT":
                if len(message) == 3:
                    req = ""
                    name = pidDict[threadID]
                    if clientDict[name][3] == True:
                        if message[1] in roomDict:
                            if message[2] in roomDict[message[1]][1]:
                                if name in roomDict[message[1]][0]:
                                    req += "OKT\n"
                                    mesaj = message[1] + " odasindan atildiniz\n"
                                    roomDict[message[1]][1].remove(message[2])
                                    roomDict[message[1]][2].append(message[2])
                                    clientDict[message[2]][2].remove(message[1])
                                    queueLock.acquire()
                                    clientDict[message[2]][1].put(mesaj)
                                    queueLock.release()
                                else:
                                    req += "REJT(engel icin yonetici olmak lazim)\n"
                            else:
                                req += "REJT(Odada boyle biri yok)\n"
                        else:
                            req += "REJT(boyle oda yok)\n"
                    else:
                        req += "REJT(giris yap)\n"
                    queueLock.acquire()
                    workQueue.put(req)
                    queueLock.release()
                else:
                    queueLock.acquire()
                    workQueue.put("Arguman eksik ya da fazla\n")
                    queueLock.release()
            elif message[0] == "SIL":
                if len(message)==2:
                    req = ""
                    name = pidDict[threadID]
                    if clientDict[name][3] == True:
                        if message[1] in roomDict:
                            if name in roomDict[message[1]][0]:
                                req += "OKS\n"
                                bildirim = message[1] + " odasi silindi.\n"
                                for i in roomDict[message[1]][0]:
                                    clientDict[i][2].remove(message[1])
                                    queueLock.acquire()
                                    clientDict[i][1].put(bildirim)
                                    queueLock.release()
                                for j in roomDict[message[1]][1]:
                                    clientDict[j][2].remove(message[1])
                                    queueLock.acquire()
                                    clientDict[j][1].put(bildirim)
                                    queueLock.release()
                                del roomDict[message[1]]
                                
                            else:
                                req += "OSS(yonetici olman lazim)\n"
                        else:
                            req += "OSS(boyle oda yok)\n"
                    else:
                        req += "OSS(giris yap)\n"
                    queueLock.acquire()
                    workQueue.put(req)
                    queueLock.release()
                else:
                    queueLock.acquire()
                    workQueue.put("Arguman eksik ya da fazla\n")
                    queueLock.release()
            elif message[0] == "YON":
                if len(message) == 3:
                    req = ""
                    name = pidDict[threadID]
                    if clientDict[name][3] == True:
                        if message[1] in roomDict:
                            if message[2] in roomDict[message[1]][1]:
                                roomDict[message[1]][1].remove(message[2])
                                roomDict[message[1]][0].append(message[2])
                                req += "OKY "+ message[2] +" yonetici yapildi.\n"
                                bildirim = message[1]+ " odasina yonetici yapildiniz\n"
                                queueLock.acquire()
                                clientDict[message[2]][1].put(bildirim)
                                queueLock.release()
                            else:
                                req += "NOY (boyle biri yok)\n"
                        else:
                            req += "NOY (boyle oda yok)\n"
                    else:
                        req += "NOY (giris yap)\n"
                    queueLock.acquire()
                    workQueue.put(req)
                    queueLock.release()
                else:
                    queueLock.acquire()
                    workQueue.put("Arguman eksik ya da fazla\n")
                    queueLock.release()
            else :
                queueLock.acquire()
                workQueue.put("ERR \n")
                queueLock.release()
    conn.close()
         
  
            
        
        
        
s = socket.socket()
host = "0.0.0.0"
port = 8080
addr_ = (host,port)
s.bind(addr_)
s.listen(100)
counter = 0
queueList = []
readThreadList = []
writeThreadList = []
personDict = {}
personIdDict = {}
roomDict = {}
while True:
    conn, addr = s.accept()
    queueLock= threading.Lock()
    workQueue = queue.Queue(100)
    queueList.append(workQueue)
    readThread_ = readThread(counter,conn,addr,personDict,personIdDict,workQueue,roomDict)
    writeThread_ = writeThread(counter,conn,addr,workQueue)
    readThreadList.append(readThread_ )
    writeThreadList.append(writeThread_ )
    readThread_.start()
    writeThread_.start()
    counter += 1



s.close()
