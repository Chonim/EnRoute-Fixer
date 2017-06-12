from tkinter import filedialog
from tkinter import messagebox
import tkinter
import csv
import shapefile
import pprint

xcol = 43   # x 좌표가 있는 열
ycol = 42   # y 좌표가 있는 열
linecol = 0
startidx = 0

newarr = []
paramarr= []
abnormalkey = []
abnormalval = []

# CSV파일 위치 가져오는 GUI 생성
top = tkinter.Tk()
top.withdraw()
file_path = filedialog.askopenfilename()

# csv파일이 맞는지 확인
# top.mainloop()
print(file_path.endswith(".csv"))
while not file_path.endswith(".csv"):
    messagebox.showerror("에러","올바른 csv파일이 아닙니다.")
    try:
        file_path = filedialog.askopenfilename()
        if file_path is None or file_path == "":
            break
    except FileNotFoundError:
        break

# 원본 대조를 위한 원본 배열
original = []

with open(file_path, 'r', encoding='utf-8') as csvfile:
    enroutereader = csv.reader(csvfile)

    def limitrows(endRow):
        i = 0
        for row in enroutereader:
            original.append(row)

            # just for testing
            # if i == endRow:
            #     break

            # increase index
            i += 1

    limitrows(1000)

s1 = list(original)

# prettify
pp = pprint.PrettyPrinter(indent=2)
# pp.pprint(s1)

# 오류값들을 찾아내서 수정
def fixabnormal() :
    prevparam = ""

    for idx, element in enumerate(s1):
        prev = s1[idx-1]
        curr = s1[idx]

        if idx > startidx :
            # get previous and current x value
            prevx = float(prev[xcol])
            currx = float(curr[xcol])

            # temp of each
            if prev[linecol] == curr[linecol] :

                # abnormal value found
                originalx = float(original[idx-1][xcol])
                # print("curr:", currx)
                # print("ori:", originalx)
                if 180 < abs(currx - originalx) < 480:

                    # param = curr[0]
                    param = ""

                    if currx < 0:
                        param = curr[linecol] + "R"
                        currx += 360
                    elif currx > 0:
                        param = curr[linecol] + "L"
                        currx -= 360

                    s1[idx][xcol] = str(currx)
                    if param != "" and prevparam != param:
                        abnormalkey.append(curr[linecol])
                        abnormalval.append(param)
                        prevparam = param

            # 극지방(168도) 처리
            # elif prev[linecol] != curr[linecol] :
            #     if int(currx) == -168:
            #         currx += 180
            #         s1[idx][xcol] = str(currx)
            #     elif int(prevx) == -168:
            #         prevx += 180
            #         s1[idx-1][xcol] = str(prevx)

            newarr.append(curr)

print("Fixing done")

# after first iteration is completed
def duplicateabnormal():
    for idx, newelement in enumerate(newarr):
        addval = 0
        if idx > 0 :
            if newelement[linecol] in abnormalkey:
                duplicatedname = abnormalval[abnormalkey.index(newelement[linecol])]
                # if newelement[0].startswith("W7"):
                #     print(newelement, duplicatedname)
                if duplicatedname.endswith("R"):
                    addval = -360
                elif duplicatedname.endswith("L"):
                    addval = 360
                else:
                    addval = 0

                duplicatedelement = list(newelement)
                duplicatedelement[linecol] += "-1"

                xfloat = float(duplicatedelement[xcol])
                duplicatedelement[xcol] = str(xfloat + addval)

                newarr.append(duplicatedelement)

# final list
# pp.pprint(newarr)

# write it in a shp file
def createshape():
    route_shp = shapefile.Writer(shapefile.POLYLINE)

    route_shp.field('AirWay_NM','C','40')
    route_shp.field('AirWay_SN','C','40')
    route_shp.field('Record_Type','C','40')
    route_shp.field('AreaCode','C','40')
    route_shp.field('SectionCode','C','40')
    route_shp.field('SubCode','C','40')
    route_shp.field('Blank_2','C','40')
    route_shp.field('Route_Iden','C','40')
    route_shp.field('Reserved_1','C','40')
    route_shp.field('Blank_3','C','40')
    route_shp.field('Sequence_num','C','40')
    route_shp.field('FIX_ID','C','40')
    route_shp.field('ICAO_Code','C','40')
    route_shp.field('SessionCode_2','C','40')
    route_shp.field('SebSection','C','40')
    route_shp.field('Cont_Rec_NO','C','40')
    route_shp.field('WayPoint_Des','C','40')
    route_shp.field('Boundary_Code','C','40')
    route_shp.field('Route_Type','C','40')
    route_shp.field('Level_','C','40')
    route_shp.field('Direction_Rest','C','40')
    route_shp.field('Cruiser_Table_IND','C','40')
    route_shp.field('EU_Indicator','C','40')
    route_shp.field('Recommand_NAVAID','C','40')
    route_shp.field('ICAO_CODE_2','C','40')
    route_shp.field('RNP','C','40')
    route_shp.field('Blank_4','C','40')
    route_shp.field('Theta','C','40')
    route_shp.field('Rho','C','40')
    route_shp.field('Outbound_Magnetic','C','40')
    route_shp.field('Route_Distance_From','C','40')
    route_shp.field('Inbound_Magnetic','C','40')
    route_shp.field('Blank_5','C','40')
    route_shp.field('Min_Alti','C','40')
    route_shp.field('Min_Alti_2','C','40')
    route_shp.field('Max_Alti','C','40')
    route_shp.field('FIX_Radius','C','40')
    route_shp.field('Reseved_2','C','40')
    route_shp.field('File_Record_No','C','40')
    route_shp.field('Cycle_Date','C','40')
    route_shp.field('L_LAN','C','40')
    route_shp.field('L_LON','C','40')

    route_shp.autoBalance = 1

    line_parts = []

    for idx, coords in enumerate(newarr):
        if idx > 0 & idx < len(newarr):
            prev = newarr[idx-1]
            line_parts.append([float(prev[xcol]),float(prev[ycol])])
            if newarr[idx][linecol] != newarr[idx-1][linecol]:
                # pp.pprint(linearr)
                if len(line_parts) > 1:
                    coords = newarr[idx-1]
                    route_shp.line(parts=[line_parts])
                    route_shp.record(
                        coords[0],
                        coords[1],
                        coords[2],
                        coords[3],
                        coords[4],
                        coords[5],
                        coords[6],
                        coords[7],
                        coords[8],
                        coords[9],
                        coords[10],
                        coords[11],
                        coords[12],
                        coords[13],
                        coords[14],
                        coords[15],
                        coords[16],
                        coords[17],
                        coords[18],
                        coords[19],
                        coords[20],
                        coords[21],
                        coords[22],
                        coords[23],
                        coords[24],
                        coords[25],
                        coords[26],
                        coords[27],
                        coords[28],
                        coords[29],
                        coords[30],
                        coords[31],
                        coords[32],
                        coords[33],
                        coords[34],
                        coords[35],
                        coords[36],
                        coords[37],
                        coords[38],
                        coords[39],
                        coords[40],
                        coords[41]
                    )
                line_parts = []

    route_shp.save('output/Enroute_fixed')
    messagebox.showinfo("완료", "shp파일 생성 완료.")

fixabnormal()
# pp.pprint(abnormalkey)
# pp.pprint(abnormalval)
# pp.pprint(paramarr)
print(len(abnormalkey))
print(len(abnormalval))
# pp.pprint(newarr)
duplicateabnormal()
createshape()

# write it on a csv file
with open("enroute_result.csv", "w", encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(newarr)
