s = 'id:0,Pos:864.0&160.0,Rot:0,Hp:100!id:1,Pos:355.22473238699166&222.20995763652888,Rot:-170.1676589976527,Hp:100!id:2,Pos:317.6969502161384&233.12447375478175,Rot:20.250754145092458,Hp:100!'
id = 0
pos = (0, 0)
rot = 0
hp = 0
# for individual_data in zombie_data.split("!"):
#        if individual_data != "":

#             for attribute in individual_data.split(","):
#                 for value in attribute.split(":"):
#                     if value[0] == "id":
#                         id = int(value[1])
#                     elif value[0] == "Pos":
#                         x, y = value[1].split("&")
#                         pos = (float(x), float(y))
#                     elif value[0] == "Rot":
#                         rot = float(value[1])
#                     elif value[0] == "Hp":
#                         hp = float(value[1])
#         print(f"Id: {id}, Pos: {pos}, Rot: {rot}, Hp: {hp}")
for individual_data in s.split("!"):
    if individual_data != "":
        print(individual_data)
        for attribute in individual_data.split(","):
            print(attribute)
            value = attribute.split(":")
            if value[0] == "id":
                id = int(value[1])
            elif value[0] == "Pos":
                x, y = value[1].split("&")
                pos = (float(x), float(y))
            elif value[0] == "Rot":
                rot = float(value[1])
            elif value[0] == "Hp":
                hp = float(value[1])
                
        print(f"Id: {id}, Pos: {pos}, Rot: {rot}, Hp: {hp}")