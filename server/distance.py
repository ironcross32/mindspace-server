"""Contains units of measurement."""

unit = 1  # A real game unit.
km = unit / 100000
m = unit / 100000000
au = km * 149597871
ly = au * 63241.077
pc = ly * 3.26156
kpc = pc * 1000
mpc = pc * 1000000

light_speed = 2.998e+8  # metres / second
light_speed *= m  # Units / second
