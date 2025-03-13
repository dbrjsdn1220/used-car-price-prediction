import requests
from bs4 import BeautifulSoup
import pandas as pd

# 차량 데이터 프레임 생성
# -----------------------------------------------
car_columns = ['차종', '가격(단위: 만)', '보험처리', '연식', '배기량', '주행거리', '연비']
url = "https://bobaedream.co.kr/mycar/popup/option_explain.php"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
data = soup.find_all("ul", class_="dic-list")

for i in range(len(data)-1):
    for j in data[i].find_all("li"):
        car_columns += [j.get_text()]

df_car = pd.DataFrame(columns=car_columns)
df_car = df_car.astype(float)

# 분석할 차량 상세 페이지 url 크롤링
# -----------------------------------------------
# 순서대로 [G80, GV80, G90, 그랜저, 쏘나타, 싼타페, 카니발, 쏘렌토, K7]
car_urls = ["https://www.bobaedream.co.kr/mycar/mycar_list.php?gubun=K&maker_no=1010&group_no=893&page=%d",
            "https://www.bobaedream.co.kr/mycar/mycar_list.php?gubun=K&maker_no=1010&group_no=1032&page=%d",
            "https://www.bobaedream.co.kr/mycar/mycar_list.php?gubun=K&maker_no=1010&group_no=958&page=%d",
            "https://www.bobaedream.co.kr/mycar/mycar_list.php?gubun=K&maker_no=3&group_no=76&page=%d",
            "https://www.bobaedream.co.kr/mycar/mycar_list.php?gubun=K&maker_no=3&group_no=69&page=%d",
            "https://www.bobaedream.co.kr/mycar/mycar_list.php?gubun=K&maker_no=3&group_no=45&page=%d",
            "https://www.bobaedream.co.kr/mycar/mycar_list.php?gubun=K&maker_no=3&group_no=76&page=%d",
            "https://www.bobaedream.co.kr/mycar/mycar_list.php?gubun=K&maker_no=3&group_no=69&page=%d",
            "https://www.bobaedream.co.kr/mycar/mycar_list.php?gubun=K&maker_no=3&group_no=45&page=%d"]
cars = []

print("시작!")
for car_type in range(len(car_urls)):
    detail_urls = []
    for i in range(1, 20):
        car_url = (car_urls[car_type] % i)
        response = requests.get(car_url)
        soup = BeautifulSoup(response.text, "html.parser")
        data = soup.find_all("p", class_="tit")
        # 예외 처리 (차량 정보가 더 이상 없는 경우)
        try:
            temp = data[0]
        except IndexError:
            break

        # 차량 상세 페이지 url 수집
        for j in range(len(data)):
            href = data[j].a['href']
            detail_urls += ["https://www.bobaedream.co.kr" + href]

    # 차량 상세 페이지로 들어가 상세 정보 크롤링
    # -----------------------------------------------
    for detail_url in detail_urls:
        print("|", end="")
        response = requests.get(detail_url)
        soup = BeautifulSoup(response.text, "html.parser")
        options = soup.find_all("span", class_="radioBox")
        # 예외 처리 (옵션 정보가 없는 차량은 Feature를 만들 수 없어 스킵)
        try:
            check = soup.find_all("div", class_="option-list-container")[0]
        except IndexError:
            print(".", end="")
            continue

        # 차종
        car = [car_type]

        # 가격(단위: 만) / 예외(렌트/리스, 계약 차량 제외)
        data = soup.find_all("b", class_="cr")
        try:
            car += [float(data[0].get_text().replace(",", ""))]
            if soup.find_all("h4", class_="tit")[1].get_text() == "렌트정보":
                print(".", end="")
                continue
            elif soup.find_all("h4", class_="tit")[1].get_text() == "리스정보":
                print(".", end="")
                continue
            elif soup.find("span", class_="price").get_text() == "[계약]":
                print(".", end="")
                continue
        except IndexError:
            print(".", end="")
            continue

        # 보험 처리 / 예외(보험 이력 없는 차 -> 판매자 주장은 무사고)
        try:
            car += [int(data[1].get_text())]
        except IndexError:
            car += [0]

        # 연식, 배기량, 주행 거리
        data = soup.find("div", class_="tbl-01 st-low").table.tbody.find_all("td")
        car += [int(data[0].get_text().split(".")[0])]
        car += [int(data[1].get_text().split(" ")[0].replace(",", ""))]
        car += [int(data[2].get_text().split(" ")[0].replace(",", ""))]

        # 연비 / 예외(연비 표시 안한 차량 -> 새차 기준 최저 평균 8.5km/l로 추가)
        try:
            car += [float(soup.find_all("strong", class_="txt")[1].get_text().split("k")[0])]
        except ValueError:
            car += [8.5]

        # 차량 옵션 데이터 수집
        data = soup.find_all("div", class_="tbl-01 st-low")
        for j in range(len(options)):
            # 예외 처리(없는 옵션 확인)
            try:
                temp = options[j].input['checked']
                car += [1]
            except KeyError:
                car += [0]
        cars.append(car)
    print('')

# cars 출력 및 csv 파일로 저장
for i in range(len(cars)):
    print(i, ": ", cars[i])
    df_car.loc[len(df_car)] = cars[i]

# 기존 파일에 데이터를 추가해서 저장
# -----------------------------------------------
df_car.to_csv('cars.csv', mode='a', header=False, index=False, encoding='cp949')

print("끝!")
