## 1. 미션 : 나만의 개발 워크스테이션 만들기
본 미션의 목표는 누구에게나 동일하고 안정적으로 실행되는 서버 개발 환경을 구축하는 것입니다. 내 컴퓨터에 Docker와 Git을 설치하고, 데이터를 안전하게 저장(Volume/Bind Mount)하는 컨테이너 웹 서버를 띄워 검증한 뒤, GitHub와 연동하여 개발 환경을 완성합니다.

## 2. 실행 환경
* OS:Windows 11 Pro (버전 25H2)
* 터미널/쉘:WSL2 (Ubuntu) / bash  
* Docker 버전: Docker version 29.6.2
* Git 버전: git version 2.55.0

## 3. 수행 항목 체크리스트 (Checklist)
터미널 기본 조작 및 파일 권한 실습
Docker 설치 및 데몬 상태 점검
Docker 기본 운영 명령(이미지, 컨테이너, 로그, 리소스) 숙달
Ubuntu 컨테이너 진입 및 내부 명령 수행
커스텀 Nginx Dockerfile 작성 및 빌드
포트 매핑을 통한 웹 서버 접속 검증
바인드 마운트 및 도커 볼륨 영속성 검증
Git 사용자 설정 및 GitHub/VS Code 연동

## 4. 프로젝트 디렉토리 구조 (Directory Structure)
본 프로젝트는 완벽한 환경 재현성을 위해 아래와 같은 표준 구조로 설계되었습니다.

```text
ro-codyssey/
├── .git/                  # Git 버전 관리 디렉토리
├── .gitignore             # Git 추적 제외 파일 목록
├── Dockerfile             # Custom Nginx 이미지 생성용 설계도
├── index.html             # 웹 서버 테스트용 메인 페이지
└── README.md              # 프로젝트 환경 구축 및 기술 문서
```
> **💡파일별 역할**
> * Dockerfile: nginx:latest를 기반으로 커스텀 index.html을 복사하고 80번 포트를 명세하는 이미지 빌드 파일
> * index.html: Docker 웹 서버 정상 동작 확인을 위한 샘플 HTML 웹 페이지
> * README.md: 기술 개념, 실행 증거, 트러블슈팅 및 환경 재현 절차가 담긴 메인 문서


## 4. 터미널 조작 및 파일 권한 실습 로그
### 4.1 기본 명령어 수행
```bash
# 1. 현재 위치한 확인 
$ pwd                          
/home/****** 

# 2. 파일 목록 확인(숨김 파일 포함)
$ ls -a                 
.  ..

# 3. 폴더 생성 및 이동
$ mkdir test
$ cd test
$ pwd
/home/******/test         

# 4. 파일 생성, 복사, 이름변경, 삭제 
$ touch test.txt
$ cp test.txt test_copy.txt
$ mv test_copy.txt renamed.txt
$ rm renamed.txt

# 5. 최종 작업 결과 확인
$ ls -l
total 4
drwxr-xr-x 2 ****** ****** 4096 Aug  2 07:59 test
-rw-r--r-- 1 ****** ******    0 Aug  2 07:59 test.txt

```

> **💡 절대 경로와 상대경로**
> * 절대경로: /home/****** 와 같이 최상위 루트(/) 디렉터리부터 시작하여 목표 파일/폴더까지의 전체 경로
> * 상대경로: ./file.txt 와 같이 현재 내가 위치한 디렉터리를 기준으로 한 경로


> **💡 절대 경로와 상대 경로의 권장 사용 사례**
> * 절대 경로 (`/home/user/app`):
>   * 개념: 최상위 루트(`/`) 디렉터리부터 시작하여 목표 파일/폴더까지의 전체 경로
>   * 권장 사례: Docker Bind Mount, CLI 자동화 스크립트, 운영(Production) 환경
>   * 실행 위치와 상관없이 항상 일정한 위치를 참조하므로 경로 오류로 인한 배포 오작동을 방지합니다.

> * 상대 경로 (`./file.txt`):
>   * 개념: 현재 내가 위치한 디렉터리를 기준으로 한 경로
>   * 권장 사례: 로컬 개인 개발 환경, 팀원 간 리포지토리 공유 시. 프로젝트 폴더의 절대 위치가 사용자마다 달라져도 코드 수정 없이 그대로 실행할 수 있습니다.
---

### 4.2 작업 디렉터리 파일 및 권한 확인/변경
> * 실험 대상: test_dir (폴더), test_file.txt (파일)

```bash
# 1. 테스트용 폴더 및 파일 생성
$ mkdir test_dir
$ touch test_file.txt                       

# 2. 변경 전 기본 권한 확인
$ ls -l
total 8                                                      
drwxr-xr-x 2 ****** ****** 4096 Aug  2 07:59 test
-rw-r--r-- 1 ****** ******    0 Aug  2 07:59 test.txt
drwxr-xr-x 2 ****** ****** 4096 Aug  2 08:02 test_dir
-rw-r--r-- 1 ****** ******    0 Aug  2 08:04 test_file.txt

# 3. 권한 변경 (폴더: 777, 파일: 755)
$ chmod 777 test_dir
$ chmod 755 test_file.txt

# 4. 변경 후 권한 확인
total 8
drwxr-xr-x 2 ****** ****** 4096 Aug  2 07:59 test
-rw-r--r-- 1 ****** ******    0 Aug  2 07:59 test.txt
drwxrwxrwx 2 ****** ****** 4096 Aug  2 08:06 test_dir
-rwxr-xr-x 1 ****** ******    0 Aug  2 08:07 test_file.txt
```
> **💡권한 분석 및 결과 해설**
* 기본 권한 상태:
> * test_dir (drwxr-xr-x): 디렉터리(d)이며, 755 권한(소유자: rwx, 그룹: r-x, 기타 사용자: r-x)이 설정되어 있습니다.
> * test_file.txt (-rw-r--r--): 일반 파일(-)이며, 644 권한(소유자: rw-, 그룹: r--, 기타 사용자: r--)이 설정되어 있습니다.
> * 권한 표기는 r(읽기=4), w(쓰기=2), x(실행=1)의 합산값입니다.
* 권한 변경 검증:
> * chmod 777 수행 후: test_dir이 drwxrwxrwx로 변경되어 모든 사용자에게 읽기/쓰기/실행 권한이 부여됨을 확인하였습니다.
> * chmod 755 수행 후: test_file.txt가 -rwxr-xr-x로 변경되어 실행 가능한 파일 상태가 됨을 확인하였습니다.

> **💡권한 변경하는 이유**
> * 서버의 중요 파일이 외부나 다른 사용자에 의해 마음대로 수정/삭제되지 않도록 보안 잠금장치를 걸고, 필요한 프로그램이나 웹 서비스만 제대로 작동할 수 있도록 권한을 주기 위해서입니다.

> **💡 한눈에 읽는 권한 기호법** 
* 맨 앞 글자: d는 디렉터리(폴더), -는 일반 파일이라는 뜻.
* 그 뒤 9자리 알파벳: 3글자씩 끊어서 [소유자 / 그룹 / 기타 사용자] 순서로 권한을 보여줌.
> * r (Read, 읽기 = 4점)
> * w (Write, 쓰기 = 2점)
> * x (eXecute, 실행 = 1점)

---
    
## 5. Docker 설치 및 기본 점검
### 5.1 Docker 환경 구축
> * 운영체제 및 환경: Windows (WSL2 기반 Docker Desktop)
> * 설치 절차:
> * PowerShell(관리자 권한)에서 wsl --install 실행 후 재부팅
> * Docker Desktop 공식 홈페이지에서 설치 파일 다운로드 및 설치

### Docker 정상 작동 확인
```bash
# 1. Docker 버전 확인 (클라이언트 및 엔진 설치 여부)
$ docker version
Client: Docker Engine - Community
 Version:           29.6.2

# 2. Docker 시스템 전체 상태 확인
$ docker info
Containers: 6
 Running: 0
 Paused: 0
 Stopped: 6
Images: 5
Server Version: 29.6.2
Operating System: Docker Desktop
```

---

### 5.3 Docker 첫 실행 테스트 (hello-world)
```bash
# 1. hello-world 이미지 다운로드 및 컨테이너 실행
$ docker run hello-world

Hello from Docker!
This message shows that your installation appears to be working correctly.

# 2. 현재 실행 중인 컨테이너 목록 확인
$ docker ps
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES

# 3. 전체 컨테이너 목록 확인 (종료된 컨테이너 포함)
$ docker ps -a
CONTAINER ID   IMAGE         COMMAND                  CREATED          STATUS                      PORTS                  NAMES
80d1151a188f   hello-world   "/hello"                 12 seconds ago   Exited (0) 11 seconds ago                          wizardly_clarke
09c83497ee07   ubuntu        "bash"                   2 days ago       Exited (127) 2 days ago                            container-B
b67d5d46ee66   ubuntu        "bash"                   2 days ago       Exited (1) 2 days ago                              container-C
5352e981c997   ubuntu        "sleep 1000"             2 days ago       Exited (0) 2 days ago                              bind-container
f09155710c48   ubuntu        "bash"                   2 days ago       Exited (0) 2 days ago                              quizzical_pare
3589b4501f03   ubuntu        "bash"                   2 days ago       Exited (0) 2 days ago                              nice_diffie
1dfbdfdefa05   web-test      "/docker-entrypoint.…"   2 days ago       Exited (255) 2 days ago     0.0.0.0:8080->80/tcp   nostalgic_cray
```
                              
#### 📸 실행 결과 캡처
![전체 컨테이너 목록 확인](https://github.com/user-attachments/assets/b76893ef-4da4-4686-9c2c-bc56750d51f0)

### 5.4 다운로드된 이미지 목록 확인
```bash
$ docker images
IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA
hello-world:latest   c3cbe1cc1aa5       25.9kB         9.49kB
my-food:latest       d74fc8b9c0c2        157MB         41.6MB
my-web:latest        5f91108394f1       92.7MB         26.1MB
ubuntu:latest        3131b4cc82a7        161MB         45.3MB    U
web-test:latest      4e727198299d        238MB         63.1MB    U
```
---

```bash
> **💡📦 Docker 이미지 vs 컨테이너 (Image vs Container) 기술 개념**
> * Docker 이미지 (Image / 불변성):
> * 컨테이너를 생성하기 위한 읽기 전용 설계도(붕어빵 틀)
> * 한번 생성된 이미지는 수정되지 않는 불변성(Immutability)을 가집니다.
> * Docker 컨테이너 (Container / 생애주기):
> * 이미지라는 설계도를 바탕으로 메모리에 격리되어 실행되는 실체(붕어빵)
> * 컨테이너 안에서 파일을 수정하거나 삭제해도 원본 이미지에는 영향을 주지 않으며, 생성(Create) ➔ 실행(Start) ➔ 중지(Stop) ➔ 삭제(Destroy)의 생애주기를 갖습니다.

### 5.5 Git 저장소 초기화 및 설정
```bash
# 1. 작업 디렉터리 내 Git 저장소 초기화
$ git init
Initialized empty Git repository in /home/******/study/.git/

# 2. Git 사용자 정보 설정
$ git config user.name "*****"
$ git config user.email "**********.*****.com"
```

#### 📸 실행 결과 캡처
![git 저장소 확인](https://github.com/user-attachments/assets/c22b373a-acdc-4e0d-baf8-c19070dc5eb1)

---

### 5.6 작업 디렉터리 파일 및 권한 확인
```bash
# 작업 폴더 내 생성된 파일 및 Git(.git) 폴더 존재 확인
$ ls -al
total 20
drwxr-xr-x  5 ****** ****** 4096 Aug  2 08:12 .
drwxr-x--- 13 ****** ****** 4096 Aug  2 08:18 ..
drwxr-xr-x  6 ****** ****** 4096 Aug  2 08:18 .git
drwxr-xr-x  2 ****** ****** 4096 Aug  2 07:59 test
-rw-r--r--  1 ****** ******    0 Aug  2 07:59 test.txt
drwxrwxrwx  2 ****** ****** 4096 Aug  2 08:06 test_dir
-rwxrwxrwx  1 ****** ******    0 Aug  2 08:07 test_file.txt
```

#### 📸 실행 결과 캡처
![작업 폴더 내 생성된 파일 및 git 폴더 존재 확인](https://github.com/user-attachments/assets/c22b373a-acdc-4e0d-baf8-c19070dc5eb1)

----

## 6. 컨테이너 실행 실습 및 분석
### 6.1 Ubuntu 컨테이너 진입 및 명령 수행
대화형 터미널 옵션(`-it`)을 사용하여 Ubuntu 컨테이너를 생성하고 내부 bash 쉘로 진입하여 기본 명령을 테스트합니다.

```bash
# 1. Ubuntu 컨테이너 생성 및 내부 접속 (-it 옵션 활용)
$ docker run -it ubuntu bash                         
root@8cf7403ce46f:/#                       # ← 내부 진입 성공

# 2. 컨테이너 내부 명령어 수행 (현재 폴더의 파일 목록 확인)
```bash
root@8cf7403ce46f:/# ls
bin  boot  dev  etc  home  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var
```
#### 📸 실행 결과 캡처!
![현재 컨테이너 목록 확인](https://github.com/user-attachments/assets/bd57cba7-65e9-4d98-be23-fec26cf3a47f)

```bash
# 3. echo 명령어 수행
root@f09155710c48:/# echo "Hello Ubuntu"           
Hello Ubuntu

# 4. 컨테이너에서 빠져나오기 (프로세스 종료)
root@f09155710c48:/# exit
```

> **💡컨테이너 종료 방식 참고**
> * exit: 컨테이너 내부 쉘을 빠져나오면서 컨테이너 프로세스를 종료시킵니다.
> * Ctrl + P + Q: 컨테이너를 백그라운드 유지 상태(Running)로 두고 터미널만 빠져나옵니다.

#### 📸 실행 결과 캡처
![우분투 컨테이너 진입](https://github.com/user-attachments/assets/200a9c98-ca72-4316-9784-9e0d1a749705)

---

## 7. 커스텀 이미지 제작 및 포트 매핑 (Nginx 웹 서버)
### 7.1 Dockerfile 작성 및 커스텀 포인트
Nginx 베이스 이미지를 활용하여 커스텀 웹 페이지를 제공하는 이미지를 생성합니다.
> * 베이스 이미지: nginx:latest
> * 주요 작업:
> * 1. 커스텀 index.html 작성
> * 2. 기본 Nginx 메인 페이지 대신 커스텀 index.html 복사
> * 3. 컨테이너 내부 웹 서비스 포트(80) 명시

```bash
# 1. 실습 파일(Dockerfile, index.html) 생성
$ touch Dockerfile index.html

# 2. VSCode로 열어서 Docker 파일 작성
$ code .

# Dockerfile
FROM nginx:latest                      # 1. Nginx 베이스 이미지 지정
COPY index.html /usr/share/nginx/html  # 2. 커스텀 HTML 파일을 컨테이너 내부로 복사
EXPOSE 80                              # 3. 80번 포트 사용 명시

# 3. 커스텀 웹페이지 내용 작성 및 확인
$ echo '<h1>Hello! This is MY Custom Docker!</h1>' > index.html  
$ cat index.html                    
<h1>Hello! This is MY Custom Docker!</h1> 

# 4. 커스텀 Docker 이미지 빌드 (-t test-web)
$ docker build -t test-web .

# 5. 이미지 생성 확인
$ docker images                     # 이미지 확인
IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA # ← 결과값  
hello-world:latest   c3cbe1cc1aa5       25.9kB         9.49kB    U
my-food:latest       d74fc8b9c0c2        157MB         41.6MB    U
my-web:latest        5f91108394f1       92.7MB         26.1MB    U
ubuntu:latest        3131b4cc82a7        161MB         45.3MB    U
web-test:latest      4e727198299d        238MB         63.1MB

```

---

### 7.2 포트 매핑 및 컨테이너 실행 검증
호스트의 `8080` 포트와 컨테이너의 `80` 포트를 매핑(`-p 8080:80`)하여 백그라운드(`-d`)로 실행합니다.

```bash
# 1. 포트 매핑 적용하여 컨테이너 실행
$ docker run -d -p 8080:80 test-web
17c127e447cfc23556ad2b6b3de9c9d29eacd97d23a0708a87a5e0008f4b8078
```

#### 📸 웹 브라우저 접속 성공 증거
> * 접속 URL: `http://localhost:8080`
![웹 브라우저 접속화면](https://github.com/user-attachments/assets/fd0506eb-9473-46c4-9a32-6928afb8a48b)

> **💡포트 매핑(8080:80)이 필요한 이유**
> * Docker 컨테이너는 격리된 가상 네트워크를 사용하므로, 외부(호스트 컴퓨터)에서 접근하려면 호스트 포트와 컨테이너 포트를 연결(-p 8080:80)해 주는 포트 포워딩 통로가 필요합니다.

---

> **💡개발 환경 재현 및 검증 절차**
> * 본 프로젝트의 실행 환경을 재현하려면 아래 순서대로 명령어를 실행하여 Docker 환경을 구성 및 검증할 수 있습니다.

```bash
# 1. 저장소 복제 및 이동
$ git clone [https://github.com/roe-e/ro-codyssey.git](https://github.com/roe-e/ro-codyssey.git)
cd ro-codyssey

# 2. 커스텀 Docker 이미지 빌드
$ docker build -t test-web .

# 3. 컨테이너 실행 (포트 매핑 8080:80)
$ docker run -d --name my-web -p 8080:80 test-web

# 4. 정상 작동 확인 (HTTP 200 OK)
$ curl -I http://localhost:8080
```

---

### 7.3 Docker 운영 명령어 수행 (상태, 로그, 리소스, 삭제)

```bash
# 1. 실행 중인 컨테이너 및 포트 매핑 상태 확인
$ docker ps
CONTAINER ID   IMAGE     COMMAND                  CREATED         STATUS         PORTS                                     NAMES
17c127e447cf   my-web    "/docker-entrypoint.…"   4 minutes ago   Up 4 minutes   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   ecstatic_raman

# 2. 종료된 것 포함한 모든 컨테이너 및 포트 매핑 상태 확인
$ docker ps -a                           # 종료된 것 포함해 모든 컨테이너 확인
CONTAINER ID   IMAGE         COMMAND                  CREATED          STATUS                        PORTS                                     NAMES
17c127e447cf   my-web        "/docker-entrypoint.…"   5 minutes ago    Up 5 minutes                  0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   ecstatic_raman
8cf7403ce46f   ubuntu        "bash"                   39 minutes ago   Exited (127) 14 minutes ago                                             pensive_bohr
80d1151a188f   hello-world   "/hello"                 55 minutes ago   Exited (0) 55 minutes ago                                               wizardly_clarke
09c83497ee07   ubuntu        "bash"                   2 days ago       Exited (127) 2 days ago                                                 container-B
b67d5d46ee66   ubuntu        "bash"                   2 days ago       Exited (1) 2 days ago                                                   container-C
5352e981c997   ubuntu        "sleep 1000"             2 days ago       Exited (0) 2 days ago                                                   bind-container
f09155710c48   ubuntu        "bash"                   2 days ago       Exited (0) 2 days ago                                                   quizzical_pare
3589b4501f03   ubuntu        "bash"                   2 days ago       Exited (0) 2 days ago                                                   nice_diffie
1dfbdfdefa05   web-test      "/docker-entrypoint.…"   2 days ago       Exited (255) 2 days ago       0.0.0.0:8080->80/tcp                      nostalgic_cray

# 3. 컨테이너 내부 실행 로그 확인
$ docker logs 17c127e447cf   
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
/docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh ~

# 4. 컨테이너 리소스 사용량 실시간 확인 (Ctrl+c로 종료)
$ docker stats                        
CONTAINER ID   NAME             CPU %     MEM USAGE / LIMIT    MEM %     NET I/O           BLOCK I/O         PIDS
17c127e447cf   ecstatic_raman   0.00%     12.71MiB / 7.71GiB   0.16%     3.88kB / 2.46kB   10.4MB / 12.3kB   13

# 5. 미사용 실행 컨테이너 정지
$ docker stop 80d1151a188f
80d1151a188f
$ docker stop 09c83497ee07
09c83497ee07
$ docker stop 5352e981c997
5352e981c997
$ docker stop f09155710c48
f09155710c48
$ docker stop 3589b4501f03
3589b4501f03
$ docker stop 1dfbdfdefa05
1dfbdfdefa05

$ docker ps -a
CONTAINER ID   IMAGE         COMMAND                  CREATED             STATUS                        PORTS                                     NAMES
17c127e447cf   my-web        "/docker-entrypoint.…"   24 minutes ago      Up 24 minutes                 0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   ecstatic_raman
8cf7403ce46f   ubuntu        "bash"                   58 minutes ago      Exited (127) 33 minutes ago                                             pensive_bohr
80d1151a188f   hello-world   "/hello"                 About an hour ago   Exited (0) 8 seconds ago                                                wizardly_clarke
09c83497ee07   ubuntu        "bash"                   2 days ago          Exited (127) 2 days ago                                                 container-B
b67d5d46ee66   ubuntu        "bash"                   2 days ago          Exited (1) 2 days ago                                                   container-C
5352e981c997   ubuntu        "sleep 1000"             2 days ago          Exited (0) 2 days ago                                                   bind-container
f09155710c48   ubuntu        "bash"                   2 days ago          Exited (0) 2 days ago                                                   quizzical_pare
3589b4501f03   ubuntu        "bash"                   2 days ago          Exited (0) 2 days ago                                                   nice_diffie
1dfbdfdefa05   web-test      "/docker-entrypoint.…"   2 days ago          Exited (255) 2 days ago       0.0.0.0:8080->80/tcp                      nostalgic_cray      

# 6. 불필요한 종료 컨테이너 정리 및 삭제
$ docker rm 09c83497ee07
09c83497ee07         
$ docker rm b67d5d46ee66
b67d5d46ee66 
$ docker rm 5352e981c997
5352e981c997
$ docker rm f09155710c48
f09155710c48
$ docker rm 3589b4501f03
3589b4501f03
$ docker rm 1dfbdfdefa05
1dfbdfdefa05

# 7. 정돈 후 최종 컨테이너 목록 확인
$ docker ps -a
CONTAINER ID   IMAGE         COMMAND                  CREATED             STATUS                        PORTS                                     NAMES
17c127e447cf   my-web        "/docker-entrypoint.…"   30 minutes ago      Up 30 minutes                 0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   ecstatic_raman
8cf7403ce46f   ubuntu        "bash"                   About an hour ago   Exited (127) 39 minutes ago                                             pensive_bohr
80d1151a188f   hello-world   "/hello"                 About an hour ago   Exited (0) 6 minutes ago                                                wizardly_clarke
```
---

## 8. 데이터 영속성(Volume) 테스트

### 8-1 바인드 마운트 (Bind Mount)
> * 호스트의 특정 디렉토리와 컨테이너 내부 폴더를 실시간 동기화하여 변경 사항을 원본에 직접 반영합니다.
```bash
# 1. 호스트(내 컴퓨터)에 테스트용 디렉토리 및 파일 생성
$ mkdir bind_test
$ cd bind_test
$ echo "Before Change" > test.txt

# 2. 바인드 마운트를 적용하여 컨테이너 실행 (-v [내 컴퓨터의 절대 경로=호스트경로]:[컨테이너 내부 경로])
$ docker run -d --name bind-container -v $(pwd):/app ubuntu sleep 1000
7855904b5345511fcdbb9f22d2075d10b9ba49748bc9f2e4a78ffe39e0b6fd1c

# 3. 컨테이너 내부 파일 내용 확인 (변경 전 데이터)
$ docker exec bind-container cat /app/test.txt
Before Change

# 4. 호스트에서 파일 내용 수정
$ echo "After Change" > test.txt

# 5. 컨테이너 내부 파일 재확인 (호스트의 변경 내용이 실시간 반영됨을 확인)
$ docker exec bind-container cat /app/test.txt
After Change
                
```
> **💡 주요 옵션 및 명령어 풀이**
> * -d: 컨테이너를 백그라운드(비동기)에서 실행
> * --name bind-container: 컨테이너 이름을 bind-container로 지정
> * -v $(pwd):/app: 호스트의 현재 작업 디렉토리($(pwd))를 컨테이너 내부의 /app 경로에 마운트(연결)합니다.
> * sleep 1000: 컨테이너가 바로 종료되지 않고 1,000초간 실행 상태를 유지하도록 지정합니다.


### 8-2 도커 볼륨 (Docker Volume)
* Docker가 관리하는 독립된 볼륨을 생성하고, 컨테이너를 삭제한 후에도 데이터가 유지되는지 영속성을 검증합니다.

```bash
# 1. 독립된 도커 볼륨 생성 (test-usb)
$ docker volume create test-usb      

# 2. 첫 번째 컨테이너(container-A)에 볼륨 마운트 후 데이터 생성
$ docker run -it --name container-A -v test-usb:/data ubuntu bash
root@ab983b329fa4:/#
root@ab983b329fa4:/# echo "Hello Volume!" > /data/secret.txt
root@ab983b329fa4:/# exit

# 3. 첫 번째 컨테이너 삭제
$ docker rm container-A
container-A

# 4. 두 번째 컨테이너(container-B)에 동일한 볼륨 마운트 후 데이터 보존 여부 확인
$ docker run -it --name container-B -v test-usb:/data ubuntu bash
root@9922419c7977:/#
root@9922419c7977:/# cat /data/secret.txt
Hello Volume!
root@9922419c7977:/# exit

```

> **💡주요 옵션 설명**
> * docker volume create test-usb: Docker 엔진이 관리하는 전용 가상 저장 공간을 생성합니다.
> * -v test-usb:/data: 생성한 볼륨을 컨테이너 내부 /data 경로에 마운트합니다.
> * docker rm container-A: 기존 컨테이너가 삭제되더라도 볼륨 내 데이터는 영구적으로 유지되는 것을 검증하였습니다.

## 9. Git 설정 및 GitHub 연동
* 개념 정리
> * Git: 로컬 컴퓨터에서 코드 변경 이력을 관리하는 버전에 제어 시스템입니다.
> * GitHub: Git 이력을 원격 서버에 저장하여 협업 및 백업을 가능하게 하는 클라우드 플랫폼입니다.

9-1. Git 설치 확인 및 기본 Config 설정
```bash
# 1. Git 설치 버전 확인
$ git --version
git version 2.55.0

# 2. Git 사용자 정보 및 기본 브랜치(main) 설정
$ git config --global user.name "*o****"
$ git config --global user.email "***n*******@*****.com"
$ git config --global init.defaultBranch main

# 3. 우분투 터미널에서 작업 폴더로 이동한 뒤 VS Code를 열어서 확인하기
$ code .
$ git config --list
user.name=*o****  (마스킹 처리)                             
user.email=***n*******@gmail.com (마스킹 처리)
init.defaultbranch=main (마스킹 처리)

```
#### 📸 실행 결과 캡처
![Git 설정 내역 확인 및 마스킹 처리완료](https://github.com/user-attachments/assets/c8739296-e111-48ff-bb1c-0936ca9b4497)

> **💡팁**
> * git config --list 출력 화면에서 목록 빠져나오기는 q 키를 누르면 됩니다.

---

9-2. Git 저장소 초기화 및 GitHub 커밋/게시
```bash
# 1. bind_test 작업 폴더를 Git 저장소(Repository)로 초기화
$ git init 
```
> **💡VSCode GUI 활용과정**
> * 좌측 메뉴의 '소스 제어' (Ctrl+Shift+G) 클릭
> * 변경 사항 확인 후 커밋 메시지 작성 및 Commit 버튼 클릭
> * Publish to GitHub 또는 Sync Changes 버튼을 클릭하여 원격 저장소 연동 완료

#### 📸 실행 결과 캡처
![Git 설정 내역 확인 및 마스킹 처리완료](https://github.com/user-attachments/assets/fff98a12-8c82-4b15-8ebc-f8e1109418d8)

---

9-3. 원격 저장소 추가 및 GitHub 푸시
```bash
$ git remote add origin https://github.com/roe-e/**-********.git
$ git push -u origin main
```
![GitHub로 푸시화면](https://github.com/user-attachments/assets/d3fb62e3-c2b4-4850-83c9-49ec5ea7d847)

---

10. 트러블슈팅
> * [이슈 1] bind_test 폴더 내에서 cd bind_test 입력 시 No such file or directory 발생
> * 원인: 이미 현재 터미널 위치가 bind_test 디렉터리 내부였기 때문에 해당 하위 폴더를 찾지 못함.
> * 해결:pwd 명령어로 현재 위치가 /home/******/bind_test임을 확인한 후, 바로 code .을 실행하여 VS Code를 열어 해결함.

> * [이슈 2] VS Code 소스 제어(나뭇가지 아이콘) 클릭 시 반응 없음
> * 원인: 작업 디렉터리 내에 Git 저장소(.git)가 초기화되지 않은 상태였음.
> * 해결: 해당 작업 폴더 터미널에서 git init 명령어를 실행하여 Git 저장소로 전환한 뒤 정상 처리함. 



