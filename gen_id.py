TEXT_VAL = """TEXT_VALUES
TEXT_NAME = NW170908_{id:04d}
TEXT_COMMENT = 
TEXT_ARRAYID = 1
TEXT_ARRAYPOS = ({x}%2C%20{y})
TEXT_OFFSETX = 0.000000
TEXT_OFFSETY = -1800.000000
TEXT_SIZE = 125.000000
TEXT_ROTATION = 0%20degree
"""
X = 20
Y = 20

output = []

for i in range(X):
    for j in range(Y):
        output.append(TEXT_VAL.format(x=i+1, y=j+1, id=1 + j + i*X))
        print(TEXT_VAL.format(x=i+1, y=j+1, id=1 + j + i*X))

f = open("ids.txt", "w")
f.write("\n".join(output))
f.close()
