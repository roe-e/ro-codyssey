## 1. 미션 : 나만의 개발 워크스테이션 만들기
이번 미션의 목표는 누구에게나 똑같이 돌아가는 코드가 안정적으로 돌아가는 서버 개발 환경을 만드는 것입니다. 내 컴퓨터에 Docker와 Git을 설치하고, 데이터를 안전하게 저장(Volume/Bind Mount)하는 컨테이너 웹 서버를 띄워 검증한 뒤, GitHub와 연동해 개발 환경을 만드는 것입니다

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
/home/***** : 루트(/) 디렉토리부터 시작하여 목표 폴더까지의 전체 주소를 의미합니다.

### 4.2 작업 디렉터리 파일 및 권한 확인 및 권한 변경
* **실험 대상:** `test_dir` (폴더), `test_file.txt` (파일)

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
-rwxrwxrwx 1 ****** ******    0 Aug  2 08:07 test_file.txt
```
#### 💡 권한 분석 및 결과 해설
* **기본 권한 상태:**
  * `test_dir` (`drwxr-xr-x`): 맨 앞의 `d`는 **디렉터리**를 의미하며, **755** 권한(소유자: 읽기/쓰기/실행, 그룹/기타: 읽기/실행)으로 설정되어 있음.
  * `test_file.txt` (`-rw-r--r--`): 맨 앞의 `-`는 **일반 파일**을 의미하며, rw-(나) : READ(4) + Write(2) = 6, r--(그룹) : READ(4) = 4, r--(남들) : READ(4) = 4로 **644** 권한(소유자: 읽기/쓰기, 그룹/기타: 읽기)으로 일반적인 웹 서버 읽기 권한에 해당함.
* **권한 변경 검증:**
  * `chmod 777` 수행 후: `test_dir`이 `drwxrwxrwx`로 변경되어 모든 사용자에게 읽기/쓰기/실행 권한이 부여됨을 확인.
  * `chmod 755` 수행 후: `test_file.txt`가 `-rwxr-xr-x`로 변경되어 실행 가능한 파일 상태가 됨을 확인. 폴더는 보통 755를 사용함.
    
## 5. Docker 설치 및 기본 점검
### 5.1 Docker 환경 구축
* **운영체제 및 환경:** Windows (WSL2 기반 Docker Desktop)
* **설치 절차:**
  1. PowerShell(관리자 권한)에서 `wsl --install` 실행 후 재부팅
  2. Docker Desktop 공식 홈페이지에서 설치 파일 다운로드 및 설치
  * *(참고: macOS 환경인 경우 OrbStack/Docker Desktop 활용)*

---

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

# 3. 전체 컨테이너 목록 확인 (종료된 hello-world 포함)
$ docker ps -a
CONTAINER ID   IMAGE         COMMAND                  CREATED          STATUS                      PORTS                  NAMES
80d1151a188f   hello-world   "/hello"                 12 seconds ago   Exited (0) 11 seconds ago                          wizardly_clarke
09c83497ee07   ubuntu        "bash"                   2 days ago       Exited (127) 2 days ago                            container-B
b67d5d46ee66   ubuntu        "bash"                   2 days ago       Exited (1) 2 days ago                              container-C
5352e981c997   ubuntu        "sleep 1000"             2 days ago       Exited (0) 2 days ago                              bind-container
f09155710c48   ubuntu        "bash"                   2 days ago       Exited (0) 2 days ago                              quizzical_pare
3589b4501f03   ubuntu        "bash"                   2 days ago       Exited (0) 2 days ago                              nice_diffie
1dfbdfdefa05   web-test      "/docker-entrypoint.…"   2 days ago       Exited (255) 2 days ago     0.0.0.0:8080->80/tcp   nostalgic_cray                                        
#### 📸 실행 결과 캡처
![전체 컨테이너 목록 확인](https://github.com/user-attachments/assets/b76893ef-4da4-4686-9c2c-bc56750d51f0)

# 4. 다운로드된 이미지 목록 확인
$ docker images
IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA
hello-world:latest   c3cbe1cc1aa5       25.9kB         9.49kB
my-food:latest       d74fc8b9c0c2        157MB         41.6MB
my-web:latest        5f91108394f1       92.7MB         26.1MB
ubuntu:latest        3131b4cc82a7        161MB         45.3MB    U
web-test:latest      4e727198299d        238MB         63.1MB    U
```
---

### 5.4 Git 저장소 초기화 및 설정
```bash
# 1. 작업 디렉터리 내 Git 저장소 초기화
$ git init
Initialized empty Git repository in /home/******/study/.git/

# 2. Git 사용자 정보 설정
$ git config user.name "*****"
$ git config user.email "**********.*****.com"
#### 📸 실행 결과 캡처
![전체 컨테이너 목록 확인](https://github.com/user-attachments/assets/c22b373a-acdc-4e0d-baf8-c19070dc5eb1)
```
```

---

### 5.5 작업 디렉터리 파일 및 권한 확인
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

#### 📸 실행 결과 캡처
![전체 컨테이너 목록 확인](https://github.com/user-attachments/assets/bd57cba7-65e9-4d98-be23-fec26cf3a47f)

----

## 6. 컨테이너 실행 실습 및 분석
### 6.1 Ubuntu 컨테이너 진입 및 명령 수행
대화형 터미널 옵션(`-it`)을 사용하여 Ubuntu 컨테이너를 생성하고 내부 bash 쉘로 진입하여 기본 명령을 테스트합니다.

```bash
# 1. Ubuntu 컨테이너 생성 및 내부 접속 (-it 옵션 활용)
$ docker run -it ubuntu bash                         
root@8cf7403ce46f:/#                       # ← 내부 진입 성공, 프롬프트가 root@컨테이너ID:/#로 바뀜

# 2. 컨테이너 내부 명령어 수행 (현재 폴더의 파일 목록 확인)
root@8cf7403ce46f:/#    $ls
bin  boot  dev  etc  home  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var

# 3. echo 명령어 수행
root@f09155710c48:/# echo "Hello Ubuntu"           
Hello Ubuntu

# 4. 컨테이너에서 빠져나오기
root@f09155710c48:/# exit

#### 📸 실행 결과 캡처
![우분투 컨테이너 진입](https://github.com/user-attachments/assets/200a9c98-ca72-4316-9784-9e0d1a749705)

```
## 7. 커스텀 이미지 제작 및 포트 매핑 (Nginx 웹 서버)
### 7.1 Dockerfile 작성 및 커스텀 포인트
Nginx 베이스 이미지를 활용하여 커스텀 웹 페이지를 제공하는 이미지를 생성합니다.
* **베이스 이미지:** `nginx:latest`
* **커스텀 포인트:** 
  1. 기본 Nginx 메인 페이지 대신 작성한 `index.html`로 교체
  2. 컨테이너 내부 웹 서비스 포트(`80`) 명시

```bash
# 1. 실습 파일(Dockerfile, index.html) 생성
$ touch Dockerfile index.html

# 2. VSCode로 열어서 Docker 파일 작성
FROM nginx:latest                      # 1. Nginx 베이스 이미지 지정
COPY index.html /usr/share/nginx/html  # 2. 커스텀 HTML 파일을 컨테이너 내부로 복사
EXPOSE 80                              # 3. 80번 포트 사용 명시

# 3. 커스텀 웹페이지 내용 작성 및 확인
$ touch index.html
$ echo '<h1>Hello! This is MY Custom Docker!</h1>' > index.html  
$ cat index.html                    
<h1>Hello! This is MY Custom Docker!</h1> 

# 4. 커스텀 Docker 이미지 빌드 (-t test-web)
$ docker build -t test-web .        

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
# 1. 1. 포트 매핑 적용하여 컨테이너 실행
$ docker run -d -p 8080:80 test-web
17c127e447cfc23556ad2b6b3de9c9d29eacd97d23a0708a87a5e0008f4b8078

#### 📸 웹 브라우저 접속 성공 증거
> **접속 URL:** `http://localhost:8080`
![컨테이너 실행하기](https://github.com/user-attachments/assets/fd0506eb-9473-46c4-9a32-6928afb8a48b)

> **💡 포트 매핑(8080:80)이 필요한 이유**
> Docker 컨테이너는 호스트 격리 환경에서 동작하므로 외부 네트워크와 연결되지 않습니다.
포트 매핑을 통해 외부(호스트)의 특정 포트로 들어오는 요청을 컨테이너 내부 포트로 전달해 주는 통로 역할을 생성해야만 브라우저에서 웹 서비스에 접속할 수 있습니다.
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

# 4. 컨테이너 리소스 사용량 실시간 확인 (docker stats, Ctrl+c로 종료)
$ docker stats                        
CONTAINER ID   NAME             CPU %     MEM USAGE / LIMIT    MEM %     NET I/O           BLOCK I/O         PIDS
17c127e447cf   ecstatic_raman   0.00%     12.71MiB / 7.71GiB   0.16%     3.88kB / 2.46kB   10.4MB / 12.3kB   13

# 5. 컨테이너 중지 후 리소스 사용량 실시간 확인 (docker stats)
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

# 6. 실습 완료된 파일 삭제 후 종료된 것 포함한 모든 컨테이너 및 포트 매핑 상태 확인 # 컨테이너 삭제 (현재 실습 제외 모두 삭제함)
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

$ docker ps -a
CONTAINER ID   IMAGE         COMMAND                  CREATED             STATUS                        PORTS                                     NAMES
17c127e447cf   my-web        "/docker-entrypoint.…"   30 minutes ago      Up 30 minutes                 0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   ecstatic_raman
8cf7403ce46f   ubuntu        "bash"                   About an hour ago   Exited (127) 39 minutes ago                                             pensive_bohr
80d1151a188f   hello-world   "/hello"                 About an hour ago   Exited (0) 6 minutes ago                                                wizardly_clarke
```
---

## 8. 데이터 영속성(Volume) 테스트

### 8-1 바인드 마운트 (Bind Mount) : 호스트의 특정 디렉토리와 컨테이너 내부 폴더를 실시간 동기화하여 변경 사항을 보관합니다.
# 1. 호스트(내 컴퓨터)에 테스트용 디렉토리 및 파일 생성
$ mkdir bind_test
$ cd bind_test
$ echo "Before Change" > test.txt

# 2. 바인드 마운트를 적용하여 컨테이너 실행 (-v [호스트경로]:[컨테이너경로])
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
> -d: 컨테이너를 백그라운드(비동기)에서 실행
> --name bind-container: 컨테이너 이름을 bind-container로 지정
> -v $(pwd):/app: 호스트의 현재 작업 디렉토리($(pwd))를 컨테이너 내부의 /app 경로와 실시간 마운트(연결)
> sleep 1000: 백그라운드 컨테이너가 즉시 종료되지 않고 1,000초간 유지되도록 명령어 실행


### 8-2 도커 볼륨 (Docker Volume)
Docker가 관리하는 독립된 볼륨을 생성하고, 컨테이너를 삭제한 후에도 데이터가 유지되는지 영속성을 검증합니다.

```bash
# 1. 독립된 도커 볼륨 생성 (test-usb)
$ docker volume create test-usb      

# 2. 첫 번째 컨테이너(container-A)에 볼륨 마운트 후 데이터 생성
$ docker run -it --name container-A -v test-usb:/data ubuntu bash
root@ab983b329fa4:/#
$ echo "Hello Volume!" > /data/secret.txt
$ exit

# 3. 첫 번째 컨테이너 삭제
$ docker rm container-A
container-A

# 4. 두 번째 컨테이너(container-B)에 동일한 볼륨 마운트 후 데이터 보존 여부 확인
$ docker run -it --name container-B -v test-usb:/data ubuntu bash
root@9922419c7977:/#
$ cat /data/secret.txt
Hello Volume!
$ exit
```
> **💡 주요 옵션 및 명령어 풀이**
> docker volume create test-usb: 도커가 자체 관리하는 독립적인 가상 저장 공간(test-usb) 생성
> -it: 컨테이너와 상호작용(Interactive)할 수 있도록 대화형 터미널(TTY)을 할당
> -v test-usb:/data: 생성해둔 도커 볼륨(test-usb)을 컨테이너 내부의 /data 경로에 마운트
> docker rm container-A: 기존 컨테이너를 완전 삭제하더라도, 연결되었던 볼륨 데이터는 호스트/도커 엔진에 영구 보관됨을 확인

## 9. Git 설정 및 GitHub 연동
** Git: 로컬 환경에서 코드 및 파일의 변경 이력을 관리하는 버전 관리 시스템
** GitHub: Git으로 관리되는 프로젝트를 원격 저장소에 보관하고 공유하는 웹 서비스

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
#### 📸 실행 결과 캡처
![Git 설정 내역 확인 및 마스킹 처리완료](https://github.com/user-attachments/assets/c8739296-e111-48ff-bb1c-0936ca9b4497)
> **💡 주요 옵션 및 명령어 풀이**
키보드에서 q 키를 눌러 명령어를 입력할 수 있는 프롬프트 상태로 돌아옵니다.
```

---

9-2. Git 저장소 초기화 및 GitHub 커밋/게시
```bash
# 4. bind_test 작업 폴더를 Git 저장소(Repository)로 초기화
$ git init 
### VS Code 좌측 메뉴의 '나뭇가지 아이콘(소스 제어, Ctrl+Shift+G) 클릭
###커밋 메시지 작성 후 Commit(커밋) 버튼 클릭
### Publish to GitHub(GitHub에 게시) 또는 Sync Changes 버튼을 클릭하여 원격 저장소 연동 완료
#### 📸 실행 결과 캡처
![Git 설정 내역 확인 및 마스킹 처리완료](https://github.com/user-attachments/assets/fff98a12-8c82-4b15-8ebc-f8e1109418d8)

