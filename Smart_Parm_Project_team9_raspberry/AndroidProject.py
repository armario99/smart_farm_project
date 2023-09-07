#source /home/armario/myenv/bin/activate
import socket
import threading
import time
import RPi.GPIO as GPIO
import Adafruit_DHT
import socket
import smbus
import RPi_I2C_driver
# DHT11 센서
DHT_PIN = 23
DHT_SENSOR = Adafruit_DHT.DHT11

HOST = ''
PORT = 8080

lcd = RPi_I2C_driver.lcd() 
# 센서 값을 전송하는 클래스
class SensorDataSender(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.sensor_data = ['senser1','senser2']
        self.lock = threading.Lock()
        self.data_num = 0
        self.sensor1 = True
        self.sensor2 = True
        self.check = False
        self.count = 0
        self.command = ""
    def add_sensor_data(self, data ,num):
        with self.lock:
            self.sensor_data[num] = (data)
    
    def stop(self):
        self.stop_flag.set()
            
    def run(self):
        def receive_data(sock):
                global PORT
                while True:
                    # 클라이언트에서 받을 문자열의 길이
                    length_data = bytearray(4)
                    sock.recv_into(length_data)
                    length = int.from_bytes(length_data, "little")

                    # 클라이언트에서 문자열 받기
                    msg_data = bytearray(length)
                    sock.recv_into(msg_data)
                    
                    # data를 더 이상 받을 수 없을 때
                    if len(msg_data) <= 0:
                        break

                    msg = msg_data.decode()
                    print(msg)
                    
                    with self.lock:
                        self.command = msg
                        print("입력 가능")
                    
                    if msg == "연결 종료":
                        sock.close()
                        print("PORT : " + str(PORT))
                        break
        while True:
            try:
                server_sock = socket.socket(socket.AF_INET)
                server_sock.bind((HOST, PORT))
                server_sock.listen(1)
            except OSError as e:
                if e.errno == 98:  # Address already in use 오류인 경우에만 다시 실행합니다.
                    self.count += 1  
                    if (self.count == 1) or (self.count == 100):  
                        print("Address already in use. Retrying...")
                    elif (self.count % 10000 == 0):
                        print("count : " + str(int(self.count)))
                            
                    continue
            self.count = 0   
            print("기다리는 중")
            
            client_sock, addr = server_sock.accept()
            print('Connected by', addr)
            data = client_sock.recv(1024)
            data = data.decode()
            print(data)

            threading.Thread(target=receive_data, args=(client_sock,)).start()                
            while True:
                try:
                    if client_sock.fileno() == -1:
                        # 클라이언트와의 연결이 이미 끊어진 경우
                        print("클라이언트와의 연결이 끊어졌습니다.")
                        break
                    print(self.sensor_data)
                    msg = ' '.join(str(data) for data in self.sensor_data)
                    print(msg)
                    data = msg.encode()
                    length = len(data)
                    # 클라이언트에 문자열 길이 보내기
                    client_sock.sendall(length.to_bytes(4, byteorder="little"))
                    self.sensor1 = True
                    self.sensor2 = True 
                    # 클라이언트에 문자열 보내기
                    client_sock.sendall(data)
                    msg = None
                    time.sleep(3)
                except:
                    break
        server_sock.close()

class LightThreadReader(threading.Thread):
    def __init__(self, data_sender):
        threading.Thread.__init__(self)
        self.bus = smbus.SMBus(1)
        self.addr = 0x48
        self.AIN0 = 0x40
        self.AIN3 = 0x43
        self.data_sender = data_sender
        self.cds_threshold = 100
        self.led_pin = 17
        self.msg = None
        self.command = ""
    
    def stop(self):
        self.stop_flag.set()
    
    def run(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.led_pin, GPIO.OUT)
        
        while True:
            with self.data_sender.lock:
                self.msg = self.data_sender.command
            
            if (self.msg == "조도 On"):
                self.command = "조도 On"
            elif (self.msg == "조도 Off"):
                self.command = "조도 Off"
            elif (self.msg == "조도 auto"):
                self.command = "조도 auto"
            else:
                self.command = self.command
                
            self.bus.write_byte(self.addr, self.AIN0)
            self.bus.read_byte(self.addr)       # dummy
            CDS = self.bus.read_byte(self.addr)
            self.bus.write_byte(self.addr, self.AIN3)
            self.bus.read_byte(self.addr)       # dummy
            VR = self.bus.read_byte(self.addr)
            data = f"조도: {CDS}" #CDS는 밝을때는 값이 작고, 어두우면 값이 커진다.
            print(f"조도 센서: {CDS}")
            if (self.command != "조도 auto"):
                if (self.command == "조도 On"):    
                    GPIO.output(self.led_pin, GPIO.LOW)
                elif (self.command == "조도 Off"):
                    GPIO.output(self.led_pin, GPIO.HIGH)
                else:
                    GPIO.output(self.led_pin, GPIO.HIGH)
            else:
                if CDS <= self.cds_threshold:
                    GPIO.output(self.led_pin, GPIO.HIGH)
                else:
                    GPIO.output(self.led_pin, GPIO.LOW)
                
            if(self.data_sender.sensor2 == True):
                    self.data_sender.add_sensor_data(data,1)
                    self.data_sender.sensor2 = False
            time.sleep(1)

# DHT11 센서 값을 읽는 클래스
class DHTSensorReader(threading.Thread):
    def __init__(self, data_sender):
        threading.Thread.__init__(self)
        self.daemon = True
        self.data_sender = data_sender
        self.msg = None
        self.command = ""
        self.command2 = ""
    
    def stop(self):
        self.stop_flag.set()
    
    def run(self):
        MOTER_A1 = 5
        MOTER_A2 = 6
        servo_pin = 22
        
        GPIO.setwarnings(False)  # 경고 메시지 비활성화
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(MOTER_A1, GPIO.OUT)
        GPIO.setup(MOTER_A2, GPIO.OUT)
        GPIO.setup(servo_pin,GPIO.OUT)
        MOTER_A1_PWM = GPIO.PWM(MOTER_A1, 20)
        MOTER_A1_PWM.start(0)
        servo_pwm = GPIO.PWM(servo_pin,50) #초기 주파수 50Hz로 설정
        servo_pwm.start(8) #초기 시작값, 반드시 입력해야됨
        
        GPIO.output(MOTER_A2, GPIO.LOW)
    
        while True:
            with self.data_sender.lock:
                self.msg = self.data_sender.command
            
            if (self.msg == "온도 On"):
                self.command = "온도 On"
                self.command2 = self.command2
            elif (self.msg == "온도 Off"):
                self.command = "온도 Off"
                self.command2 = self.command2
            elif (self.msg == "온도 auto"):
                self.command = "온도 auto"   
                self.command2 = self.command2 
            elif (self.msg == "습도 On"):
                self.command2 = "습도 On"
                self.command = self.command
            elif (self.msg == "습도 Off"):
                self.command2 = "습도 Off"
                self.command = self.command
            elif (self.msg == "습도 auto"):
                self.command2 = "습도 auto"
                self.command = self.command    
            else:
                self.command = self.command
                self.command2 = self.command2
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            
            if humidity is None:
                print("humidity error")
            else:
                if (self.command2 != "습도 auto"):
                    if (self.command2 == "습도 On"):
                        servo_pwm.ChangeDutyCycle(9)
                        time.sleep(0.5)
                    elif (self.command2 == "습도 Off"):
                        servo_pwm.ChangeDutyCycle(8)
                        time.sleep(0.5)
                    else:
                        if humidity > 60 :
                            servo_pwm.ChangeDutyCycle(8)
                            time.sleep(0.5)
                        else:
                            servo_pwm.ChangeDutyCycle(9)
                            time.sleep(0.5)
                else:
                    if humidity > 60 :
                        servo_pwm.ChangeDutyCycle(8)
                        time.sleep(0.5)
                    else:
                        servo_pwm.ChangeDutyCycle(9)
                        time.sleep(0.5)
            if temperature is None:
                print("temperature error")
            else:
                duty = 0
                if (self.command != "온도 auto"):
                    if (self.command == "온도 On"):
                        duty = 30 
                    elif (self.command == "온도 Off"):
                        duty = 0
                    else:
                        if temperature >= 25 and temperature < 27:
                            duty = 20
                        elif temperature >= 27 and temperature < 29:
                            duty = 30
                        elif temperature >= 29 and temperature < 32:
                            duty = 60
                        else:
                            duty = 0
                        duty = 0
                else:
                    if temperature >= 25 and temperature < 27:
                        duty = 20
                    elif temperature >= 27 and temperature < 29:
                        duty = 30
                    elif temperature >= 29 and temperature < 32:
                        duty = 60
                    else:
                        duty = 0
                    duty = 0
                
                MOTER_A1_PWM.ChangeDutyCycle(duty)
                
            if humidity is not None and temperature is not None:
                print(f"DHT11 센서 - 온도: {temperature:.2f}°C, 습도: {humidity:.2f}%")
                data = f"온도: {temperature:.2f} °C 습도: {humidity:.2f} %"
                #data = f"습도: {humidity:.2f}%"
                print(self.data_sender.sensor1)
                if(self.data_sender.sensor1 == True):
                    self.data_sender.add_sensor_data(data,0)
                    self.data_sender.sensor1 = False
                lcd.lcd_display_string(f"Temp:{temperature:.2f}*C",1)
                lcd.lcd_display_string(f"humidity:{humidity:.2f}%",2)
                
            else:
                print("DHT11 센서 - 값 읽기 실패")
            
            
            time.sleep(1)
            
class BuzzerThread(threading.Thread):
    def __init__(self,data_sender):
        threading.Thread.__init__(self)
        self.buzzer_pin = 18
        self.data_sender = data_sender
        self.msg = None
        self.command = ""
        self.scale = [262, 294, 330, 349, 392, 440, 494]
        self.twinkle_star = [1,1,5,5,6,6,5,4,4,3,3,2,2,1,
                             5,5,4,4,3,3,2,5,5,4,4,3,3,2,
                             1,1,5,5,6,6,5,4,4,3,3,2,2,1]
    def stop(self):
        self.stop_flag.set()
        
    def run(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.buzzer_pin, GPIO.OUT)
        pwm = GPIO.PWM(self.buzzer_pin, 1.0)
        pwm.start(90.0)

        while True:
            with self.data_sender.lock:
                self.msg = self.data_sender.command
            
            if (self.msg == "음악 Off"):
                self.command = "음악 Off"
            elif (self.msg == "음악 1"):
                self.command = "음악 1"
            elif (self.msg == "음악 2"):
                self.command = "음악 2"
            else:
                self.command = self.command
        
            if (self.command == "음악 1"):
                for i in range(len(self.twinkle_star)):
                    print(self.scale[self.twinkle_star[i]])
                    #pwm.ChangeFrequency(self.scale[self.twinkle_star[i]])
                    time.sleep(0.5)
                pwm.stop()
            elif (self.command == "음악 2"):
                for i in range(len(self.twinkle_star)):
                    print(self.scale[self.twinkle_star[-i]])
                    #pwm.ChangeFrequency(self.scale[self.twinkle_star[-i]])
                    time.sleep(0.5)
                pwm.stop()
            else:
                pass
            
# 메인 코드
if __name__ == "__main__":
    try:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        data_sender = SensorDataSender()
        dht_reader = DHTSensorReader(data_sender)
        light_reader = LightThreadReader(data_sender)
        buzzer_thread = BuzzerThread(data_sender)
        
        data_sender.start()
        dht_reader.start()
        light_reader.start()
        buzzer_thread.start()
        
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("프로그램을 종료합니다.")
        lcd.lcd_clear()
        lcd.backlight(0)
        data_sender.stop()
        dht_reader.stop()
        light_reader.stop()
        buzzer_thread.stop()
        lcd.lcd_clear()
        lcd.backlight(0)
        
        data_sender.join()
        dht_reader.join()
        light_reader.join()
        buzzer_thread.join()
        
        lcd.lcd_clear()
        lcd.backlight(0)
        
    finally:
        lcd.lcd_clear()
        lcd.backlight(0)
        GPIO.cleanup()
