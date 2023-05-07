# Payhere 교육 과제 🔥

## ***Introduction*** ✔

> 사장님은 카페를 운영하는 사장님입니다. 
> 사장님은 상품을 등록해서 가게를 운영하고 싶습니다. 
> 아래의 요구사항을 만족하는 DB 테이블과 REST API를 만들어주세요. 

## ***Requirements***

>1. 사장님은 시스템에 휴대폰번호와 비밀번호 입력을 통해서 회원 가입을 할 수 있습니다. 
>    - 사장님의 휴대폰 번호를 올바르게 입력했는지 확인해주세요
>    - 비밀번호를 안전하게 보관할 수 있는 장치를 만들어주세요
>2. 사장님은 회원 가입이후, 로그인과 로그아웃을 할 수 있습니다. 
>3. 사장님은 로그인 이후 상품관련 아래의 행동을 할 수 있습니다. 
>    1. 상품의 필수속성(required)은 다음과 같습니다. 
>        1. 카테고리
>        2. 가격
>        3. 원가 
>        4. 이름 
>        5. 설명
>        6. 바코드
>        7. 유통기한 
>       8. 사이즈 : small or large
>    2. 사장님은 상품을 등록할 수 있습니다. 
>    3. 사장님은 상품의 속성을 부분 수정할 수 있습니다. 
>    4. 사장님은 상품을 삭제 할 수 있습니다
>    5. 사장님은 등록한 상품의 리스트를 볼 수 있습니다. 
>        - cursor based pagination 기반으로, 1page 당 10개의 상품이 보이도록 구현
>    6. 사장님은 등록한 상품의 상세 내역을 볼 수 있습니다. 
>    7. 사장님은 상품 이름을 기반으로 검색할 수 있습니다. 
>        - 이름에 대해서 like 검색과 초성검색을 지원해야 합니다.
>        - 예) 슈크림 라떼 → 검색가능한 키워드 : 슈크림, 크림, 라떼, ㅅㅋㄹ, ㄹㄸ
>4. 로그인하지 않은 사장님의 상품 관련 API에 대한 접근 제한 처리가 되어야 합니다.

### ***Summary*** 🔽
> - Project 소개
>   - 상품 CRUD 구현
>   - DjangoRestFramework를 이용하여 회원, 상품 관리 REST API 서버 구현
>   - JWT를 이용한 Authentication 및 Authorization 구현


### ***Requirments*** 🤔
> - BACKEND(Djagno Authentication Server)
>   - django~=4.2.1
>   - django-environ==0.10.0
>   - djangorestframework~=3.14.0
>   - djangorestframework-simplejwt~=5.2.2
>   - mysql-connector-python==8.0.33
>   - PyMySQL==1.0.3

> - DataBase
>   - MySQL:5.7

<br>

### ***IDE*** 🥢
> - BACKEND
>   - Pycharm Professional
>   - VScode
>   - Postman
>   - MySQL Workbench
>   - Docker


<br>

### ***Backend End-points*** 
> Resource modeling(수정 예정)
> 
> 1️⃣ 회원 관련 API
> 
>   |  HTTP |  Path |  Method |  Permission |  목적 |
>   | --- | --- | --- | --- | --- |
>   |**POST** |/accounts/signup/|CREATE| AllowAny |사용자 회원가입|
>   |**POST** |/accounts/login/|NONE| AllowAny |사용자 로그인, access_token, refresh_token 생성 및 반환|
>   |**POST** |/accounts/logout/|NONE| IsAuthenticated |사용자 로그아웃, BlacklistedToken에 refresh_token 추가|
> 
> 
> 2️⃣ 상품 관련 API
> 
>   |  HTTP |  Path |  Method |  Permission |  목적 |
>   | --- | --- | --- | --- | --- |
>   |**GET**, **POST** |/products/|LIST, CREATE| IsOwner and Access_token |상품 등록 및 등록한 상품들 확인|
>   |**GET** |/products/?name={검색할 이름}|LIST| IsOwner and Access_token |쿼리 스트링에 맞는 상품의 이름 초성 혹은 like 검색|
>   |**GET**, **PATCH**, **DELETE** |/products/<int:pk>/|RETRIEVE, UPDATE, DESTORY| IsOwner and Access_token |자신의 루틴 단건 확인, 수정, 삭제|

<br>

### ***ERD*** 🏳

> ![image](https://user-images.githubusercontent.com/95459089/236669747-c21cf87d-a747-4e4e-9754-b57a890cdc75.png)

<br>

### ***process*** 🚀
>
> #### 회원관련 API
> ##### 사용자 회원가입
> - 요청
>
> ![image](https://user-images.githubusercontent.com/95459089/236670902-67cff547-fd65-477e-8555-6161a9e1079c.png)
> - 응답
>
> ![image](https://user-images.githubusercontent.com/95459089/236670917-d35bac50-63c9-4011-9f48-4437db0f1c32.png)
> 
> ##### 사용자 로그인
>
> - 요청
>
> ![image](https://user-images.githubusercontent.com/95459089/236670936-a4121266-5eb8-4fce-aaa4-5b3960ac7597.png)
> - 응답
> 
> ![image](https://user-images.githubusercontent.com/95459089/236670954-1a5d98a7-8ebe-4362-b97e-edb012f1ee3f.png)
>
> ##### 로그아웃
>
> - access_token 세팅
>
> ![image](https://user-images.githubusercontent.com/95459089/236670995-fda91e64-6cc4-49ac-83d3-11a32ac0cb9f.png)
>
> - 요청
>
> ![image](https://user-images.githubusercontent.com/95459089/236671056-a668f7a9-e858-4547-a604-23b45be1e1ea.png)
>
> - 응답
>
> ![image](https://user-images.githubusercontent.com/95459089/236671073-8574550d-13bc-4342-889d-a362ae9d151a.png)
>
> #### 상품 관련 API
> - access_token 세팅
> 
> ![image](https://user-images.githubusercontent.com/95459089/220854533-dfb0b38d-940a-40e6-8276-b779fc4c01b8.png)
> 
> ##### 상품 등록
> 
> - 요청 
>
> ![image](https://user-images.githubusercontent.com/95459089/236671135-493eba6c-08c4-4235-b0e4-6dbb4556f366.png)
>
> - 응답
>
> ![image](https://user-images.githubusercontent.com/95459089/236671157-50f63a14-5818-4cb3-91c3-b49e4bfdbde1.png)
>
> ##### 상품 목록
>
> - 요청
> 
> ![image](https://user-images.githubusercontent.com/95459089/236671173-0a0a0174-c953-4f71-892f-789f5b06c624.png)
>  
> - 응답
> 
> ![image](https://user-images.githubusercontent.com/95459089/236671185-f5941dee-182a-46af-b1e3-578ac7c13710.png)
>
> ##### 상품 상세 조회
>
> - 요청
> 
> ![image](https://user-images.githubusercontent.com/95459089/236671578-65eaf998-3499-479f-a301-2c4c44d29cf7.png)
>
> - 응답
>
> ![image](https://user-images.githubusercontent.com/95459089/236671589-ea3e7c76-f922-4bf3-ba8d-1dedbae71a50.png)
>
> ##### 상품 부분 수정
>
> - 요청
>
> ![image](https://user-images.githubusercontent.com/95459089/236671608-aaf92406-4ff1-4256-a3db-b9db4061437e.png)
>
> - 응답
>
> ![image](https://user-images.githubusercontent.com/95459089/236671623-1efd8bef-b4fe-4205-95a9-f7f8c642ec52.png)
>
> ##### 상품 삭제
>
> - 요청
>
> ![image](https://user-images.githubusercontent.com/95459089/236671652-72c21c53-1be1-49e7-b308-bca244e4e218.png)
>
> - 응답
>
> **status code만 204 no content로 전달**
> 
>
> ##### 상품 초성 검색
>
> - 요청
>
> ![image](https://user-images.githubusercontent.com/95459089/236671745-1c6fdb6f-d922-485c-94f3-8c7510d66054.png)
>
> - 응답
>
> ![image](https://user-images.githubusercontent.com/95459089/236671754-fc6917a9-759d-4af4-8555-87eca5a0c4cb.png)
>
> ##### 상품 like 검색
>
> - 요청
>
> ![image](https://user-images.githubusercontent.com/95459089/236671781-43751641-f846-4ffe-97b0-e76398bab932.png)
>
> - 응답
>
> ![image](https://user-images.githubusercontent.com/95459089/236671789-681a057a-5c20-43be-8aa3-5e2d07b1fa4d.png)
>
> ##### 상품 조회 (cursor based pagination)
>
> - 요청
>
> ![image](https://user-images.githubusercontent.com/95459089/236671938-aec42547-1525-49ae-b2fc-9dec4d4228f8.png)
>
> - 응답
>
> ![image](https://user-images.githubusercontent.com/95459089/236671949-5113799d-0674-4259-a9fd-fb31fe4fa3d6.png)
> 
> **상품 목록이 10개가 넘어가는 경우 해당**
>

### Installation

**Backend**
>
> <br>
> 
> **1. Payhere repository clone**
> 
> ```bash
> git clone https://github.com/donghyeok1/payhere.git
> ```
>
> **2. backend 환경 설정**
>
> ```bash
> cd payhere
> ```
>
> **2-1 환경 세팅**
>
> [django secret key 생성 사이트](https://djecrety.ir/)
>
> ![image](https://user-images.githubusercontent.com/95459089/236672311-f2839045-0ecd-4175-8e6a-f723e85fbf65.png)
>
> - 이동 후, Generate 클릭 후 키 복사
> - .env 파일
>
> ![image](https://user-images.githubusercontent.com/95459089/236672353-274c6933-0edb-47ef-abd2-addd7fc95370.png)
>
> - **위의 사이트에서 생성한 secret key를 SECRET_KEY= 넣어주기**
> - **나머지는 위의 그림처럼 입력**
> 
>
> **2-2 컨테이너 실행**
> - docker-compose.yml이 있는 디렉토리로 이동
> 
> ```bash
> docker compose up
> ```
> 
> **3 결과**
> - 이미지를 전부 가져오고, 빌드하는 과정에서 backend는 mysql과 연동 오류를 없애기 위해 dockerfile 실행 후, 20초의 sleep을 가지고 command를 실행한다.
> - 조금 기다린 후 확인
> - MySQL Workbench 접속.(127.0.0.1, root, qwer1234)
>
> ![image](https://user-images.githubusercontent.com/95459089/236672616-102bf871-6303-4426-805e-74bf498d25f9.png)
> 
> - web 데이터베이스가 생기고, migrate가 잘 된 것을 확인할 수 있다.
> - payhere-backend 컨테이너 log 확인
> 
> ![image](https://user-images.githubusercontent.com/95459089/236672651-0e6bd5f3-50e7-435b-ae57-9e0a2b3309e6.png)
> 
> - 서버가 잘 구동되는 것을 확인할 수 있다.
> 

