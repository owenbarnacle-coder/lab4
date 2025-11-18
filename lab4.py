from machine import UART, Pin
import _thread
import utime

# UART SETUP
uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))


message_queue = []
queue_lock = _thread.allocate_lock()

KEEP_ALIVE_INTERVAL = 5
last_send_time = utime.time()



def input_thread():
    global message_queue
    while True:
        text = input()              # blocking call, safe in thread
        with queue_lock:
            message_queue.append(text)


# Start the input thread
_thread.start_new_thread(input_thread, ())



# MAIN LOOP : handles UART + keepalive + message sending

print("Chat Pico Ready.")
print("Type messages and press ENTER.\n")

while True:
    # ---- CHECK FOR INCOMING UART DATA ----
    if uart.any():
        incoming = uart.readline()
        if incoming:
            try:
                print("[RX] " + incoming.decode().strip())
            except:
                print("[RX] <unreadable data>")

    # ---- CHECK FOR USER MESSAGES FROM INPUT THREAD ----
    with queue_lock:
        if message_queue:
            user_msg = message_queue.pop(0)
            send = "MSG: " + user_msg + "\n"
            uart.write(send)
            print("[TX] " + user_msg)
            last_send_time = utime.time()

    # ---- SEND KEEP-ALIVE IF NEEDED ----
    now = utime.time()
    if now - last_send_time > KEEP_ALIVE_INTERVAL:
        h, m, s = utime.localtime()[3:6]
        keepalive = "KEEPALIVE: {:02d}:{:02d}:{:02d}\n".format(h, m, s)
        uart.write(keepalive)
        print("[TX] Sent keep-alive.")
        last_send_time = now

    utime.sleep(0.05)