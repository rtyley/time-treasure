import rp2
from machine import Pin
from rp2 import PIO

print("Hello, Pi Pico!")

beginBitTransmissionInterruptNum=1


beginBitTransmissionFlag = 1
bitTransmissionStageCompleteFlag = 2

finishHighBitFlag = 3
finishSSBitFlag = 4

@rp2.asm_pio()
def clockRock():
    irq(0)
    set(x, 20)
    label("chill")
    jmp(x_dec, "chill")  [31]

@rp2.asm_pio(set_init=[PIO.OUT_LOW])
def beginBitTransmission():
    wait(1, irq, 1)
    set(x,5)
    label("pulse_cycle")
    wait(1, irq, 0)
    set(pins,1)
    wait(1, irq, 0)
    set(pins,0)
    jmp(x_dec, "pulse_cycle")
    set(x, 9)
    label("blank_cycle")
    wait(1, irq, 0)
    wait(1, irq, 0)
    jmp(x_dec, "blank_cycle")
    irq(2)

@rp2.asm_pio()
def finishHighBitPause():
    wait(1, irq, 3)
    set(x, 10)
    label("blank_cycle")
    wait(1, irq, 0)
    wait(1, irq, 0)
    jmp(x_dec, "blank_cycle")
    irq(2)

@rp2.asm_pio()
def finishSSBitPause():
    wait(1, irq, 4)
    set(x, 28)
    label("blank_cycle")
    wait(1, irq, 0)
    wait(1, irq, 0)
    jmp(x_dec, "blank_cycle")
    irq(2)


@rp2.asm_pio()
def experiment():
    pull()
    out(isr, 16)
    irq(1) # write out SS bit
    wait(1, irq, 2)
    # TODO perform SS bit pause

    label("transmit-bit")
    out(x, 1)
    jmp(not_x, "bit-transmit-finished")
    irq(3) # perform high bit pause
    wait(1, irq, 2)
    label("bit-transmit-finished")
    jmp(not_osre, "transmit-bit")

    irq(1) # write out SS bit
    wait(1, irq, 2)
    # TODO perform SS bit pause

    



rp2.StateMachine(0, clockRock, freq=8000).active(1)

# Low bit consists of 6 cycles of IR and 10 “cycles” of pause
# High bit of 6 cycles IR and 21 “cycles” of pause
# Start/Stop bit of 6 cycles IR and 39 “cycles” of pause.
rp2.StateMachine(1, beginBitTransmission, freq=2000, set_base=Pin(0)).active(1)
rp2.StateMachine(2, finishHighBitPause, freq=2000).active(1)
#rp2.StateMachine(3, finishSSBitPause, freq=2000).active(1)

sm = rp2.StateMachine(3, experiment, freq=2000)
sm.active(1)

