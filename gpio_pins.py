import gpiod

from gpiod.line import Direction, Value

def write_pin(pinno: int, val: bool):
    with gpiod.request_lines(
        "/dev/gpiochip4",
        config={
            pinno: gpiod.LineSettings(
                direction=Direction.OUTPUT, output_value=Value.ACTIVE
            )
        },
    ) as request:
        request.set_value(pinno, Value.ACTIVE if val else Value.INACTIVE)
