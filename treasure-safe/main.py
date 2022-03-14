import rp2
from machine import Pin
from rp2 import PIO

print("Hello, Pi Pico!")

beginBitTransmissionInterruptNum=1

beginBitTransmissionFlag = 1
bitTransmissionStageCompleteFlag = 2


@rp2.asm_pio(set_init=[PIO.OUT_LOW],sideset_init=[PIO.OUT_LOW])
def beginBitTransmission():
    wait(1, irq, 1)
    set(x, 4).side(1) [6]
    nop().side(0) [6]
    label("pulse_cycle")
    nop().side(1) [6]
    nop().side(0) [5]
    jmp(x_dec, "pulse_cycle")

    set(x, 19) [6] # one less half-cycle loop (19 rather than 20) to incorporate the cost of the 'set' instruction
    label("blank_cycle")
    jmp(x_dec, "blank_cycle") [6] # half-38kHz cycle lasts 7 instructions - 'jmp' is 1, other 6 are pause
    irq(2)

@rp2.asm_pio(set_init=[PIO.OUT_LOW])
def experiment():
    pull(block)
    set(pins,1)
    out(isr, 16) # LPF message is only 16 bits
    irq(1) # write out SS bit
    wait(1, irq, 2)
    # perform ss-bit pause (for start-bit of message)
    set(x, 27) [13] # one less loop (28 rather than 29) to incorporate the cost of the 'set' instruction
    label("additional_start_bit_pause")
    jmp(x_dec, "additional_start_bit_pause") [13] # 38kHz cycle lasts 14 instructions - 'jmp' is 1, other 13 are pause

    label("transmit-bit")
    out(x, 1)
    irq(1) # write out bit start
    wait(1, irq, 2)
    jmp(not_x, "bit-transmit-finished")

    set(x, 9) [13] # one less loop (10 rather than 11) to incorporate the cost of the 'set' instruction
    label("additional_high_bit_pause")
    jmp(x_dec, "additional_high_bit_pause") [13] # 38kHz cycle lasts 14 instructions - 'jmp' is 1, other 13 are pause

    label("bit-transmit-finished")
    jmp(not_osre, "transmit-bit")

    irq(1) # write out SS bit
    wait(1, irq, 2)
    # perform ss-bit pause (for stop-bit of message)
    set(x, 27) [13] # one less loop (28 rather than 29) to incorporate the cost of the 'set' instruction
    label("additional_stop_bit_pause")
    jmp(x_dec, "additional_stop_bit_pause") [13] # 38kHz cycle lasts 14 instructions - 'jmp' is 1, other 13 are pause
    set(pins,0)




frequency = round(125000000/(1645/7))
# Low bit consists of 6 cycles of IR and 10 “cycles” of pause
# High bit of 6 cycles IR and 21 “cycles” of pause
# Start/Stop bit of 6 cycles IR and 39 “cycles” of pause.
rp2.StateMachine(0, beginBitTransmission, freq=frequency, set_base=Pin(0),sideset_base=Pin(0)).active(1)

sm = rp2.StateMachine(1, experiment, freq=frequency, set_base=Pin(1))
sm.active(1)
sm.put(123)