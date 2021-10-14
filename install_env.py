#!/usr/bin/python
# coding:utf8
# @author:nuex,http://handsome.ink
# for centos7 x64  mini install

# from config import INSTALL_PATH, NGINX_VERSION, REDIS_VERSION, MySQL_PASSWORD,MYSQL_USER_NAME, APOLLO_VERSION, APOLLO_PROTEL_IP, \
#     MySQL_IP_PORT,MAVEN_VERSION,FUNCTION_MAPPING,REDIS_CLUSTER_PORT,RUBY_VERSION,IP,FASTDFS_VERSION,LIBFASTCOMMON_VERSION,FASTDFS_TRACKER_PORT,\
#     FASTDFS_TRACKER_BASE_PATH,FASTDFS_TRACKER_HTTP_SERVER_PORT,FASTDFS_STORAGE_BASE_PATH,FASTDFS_STORAGE_STORE_PATH0,FASTDFS_STORAGE_TACKER_SERVER,\
#     FASTDFS_STORAGE_HTTP_SERVER_PORT,FASTDFS_STORAGE_PORT
from config import *
from utils import ModifyConfig,ModifyRedisConf,GitHosts,progress_bar
import sys, os, commands,stat,subprocess
#日志模块
import logging
logger = logging.getLogger(__file__[:-3].split('/')[-1])
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.FileHandler(__file__[:-3].split('/')[-1]+".log")
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(handler)
logger.addHandler(console)
printi=logger.info
printe=logger.error
printw=logger.warning
try:
    import sh
except:
    os.system('yum -y install epel-release')
    os.system('yum -y install python-pip')
    os.system('pip install sh')
    try:
        import sh
    except:
        printi ('import sh module failed')

FEED0="""

        location /group1/M00 {
            alias /usr/local/soft/fastdfs/storage/file/data;
        }

"""
FEED="""

        location ~/group([0-9])/M00 {
            ngx_fastdfs_module;
        }

"""





class Method(object):
    def __init__(self,path,version):
        self.path=path
        self.version=version
        self.exists=os.path.exists
        if not os.path.exists(self.path):
            os.system('mkdir '+self.path)
        os.chdir(self.path)

    def open_firewall(self,port):  # 开启端口
        os.system("firewall-cmd --zone=public --add-port={}/tcp --permanent".format(port).replace('\n',''))
        os.system("firewall-cmd --reload")


    # 预安装环境升级
    def install_tools(self):
        printi('\033[32mstart install and upgrade environment...\033[0m')
        cmd = 'yum -y install gcc wget automake autoconf unzip libtool make gcc-c++ pcre* zlib* openssl openssl-devel libevent erlang'
        if self.exec_cmd(cmd):
            pass
        else:
            printi('\033[31minstall environment failed....\033[0m')
            sys.exit()

    def exec_cmd(self,cmd,igore_error=1):
        stat, output = commands.getstatusoutput(cmd)
        printi(output)
        if stat == 0:
            return True
        else:
            if not igore_error:
                with open('install_error.log', 'a') as a:
                    a.write('%s \n' % output)
            return False

    @property
    def create_path(self):
        cmd = 'mkdir {}'.format(self.path)
        if self.exec_cmd(cmd):
            pass
        else:
            printi('\033[31create path failed maybe exists....\033[0m')
        os.chdir(self.path)  # 切换工作路径到path
        # sys.exit()

class AutoEnvironment(object):
    def __init__(self):
        self.command_status={}
        self.path_status={}
    def check_path(self,path):
        """
        :param path:full path example:/user/local/soft
        :return:
        """
        printi('\033[1;32;40m')
        printi('-'*50+'check {}'.format(path)+'-'*50)
        stat, output = commands.getstatusoutput('cd {}'.format(path))
        if stat:#
            printi('\033[1;31;40m')
            printi("{} is not exist".format(path))
            self.path_status[path]=0
        else:
            printi('\033[1;32;40m')
            printi('{} is exist'.format(path))


    def check_command(self,command):
        """
        :param command:command example:javac
        :return:
        """
        printi('\033[1;32;40m')
        printi('-'*50+'check {}'.format(command)+'-'*50)
        stat, output = commands.getstatusoutput(command)
        if stat:#
            printi('\033[1;31;40m')
            printi("command {} is not exist".format(command))
            self.command_status[command]= 0
        else:
            printi('\033[1;32;40m')
            printi('command {} is exist'.format(command))
            self.command_status[command] = 1


    def create_path(self):
        for path,status in self.path_status.items():
            if not status:
                printi('\033[1;32;40m')
                printi("start create path: {}".format(path))
                os.popen("mkdir {}".format(path))

    def install_command(self):
        for command,status in self.command_status:
            if not status:
                printi('\033[1;32;40m')
                printi("start install command: {}".format(command))
                eval(FUNCTION_MAPPING[command])#执行安装方法
    @property
    def start(self):
        printi('start')
        pass

#添加nginx服务到系统并开机启动
def nginx_service():#暂时弃用
    pass
"""    download_cmd = 'wget -c ftp.sosolinux.com/nginx/nginx.sh'
    if exec_test(download_cmd):
        os.system('chmod u+x nginx.sh')
        os.system('cp -p ./nginx.sh /etc/init.d/nginx')
        # 添加到开机启动
        os.system('chkconfig --level 35 nginx on')
        os.system('/etc/init.d/nginx restart')
    else:
        os.system('rm -rf nginx.sh')
        print
        '\033[31mdownload nginx.sh failed... \033[0m'
        os.exit()"""

class FUNC_MAP(object):
    def __init__(self, map=None):
        if map is None:
            map = []
        self.map=map

    def register_map(self,dic):
        for k,v in dic.items():
            self.map.append({k,v})

    def execute(self):
        printi('execute method :{}'.format(self.map))
        execute_func=[dic.keys()[0]+'()' for dic in self.map if dic.values()[0]]
        printi(execute_func)
        for func in execute_func:
            printi('start install {}'.format(func[:-2]))
            eval(func)
            printi('install {} finish'.format(func[:-2]))

class I_nginx(Method):
    @property
    def install(self):
        tar_cmd = 'tar -zxf nginx-{}.tar.gz'.format(self.version)
        if self.exec_cmd(tar_cmd):
            # chroot_cmd = 'cd nginx-1.4.2 && '
            os.chdir('./nginx-{}'.format(self.version))
            # ' --user=nginx --group=nginx \
            config_cmd = './configure --prefix={}nginx \
            --with-http_stub_status_module \
            --with-http_ssl_module \
            --with-http_gzip_static_module \
            --with-http_flv_module'.format(self.path)
            # install_cmd = chroot_cmd + config_cmd
            if FASTDFS_TRACKER or FASTDFS_STORAGE or FASTDFS_CLIENT:
                self.open_firewall(80)
                if self.exists('fastdfs-nginx-module-5e5f3566bbfa57418b5506aaefbe107a42c9fcb1.zip'):
                    printi('file exists')
                else:
                    progress_bar('start download fastdfs-nginx-module from github......')
                    os.system('wget --no-check-certificate https://github.com/happyfish100/fastdfs-nginx-module/archive/5e5f3566bbfa57418b5506aaefbe107a42c9fcb1.zip &&mv fastdfs-nginx-module-5e5f3566bbfa57418b5506aaefbe107a42c9fcb1.zip fastdfs-nginx-module-{}'.format(
                        FASTDFS_NGINX_MODULE_VERSION))
                    # 解压并重命名
                    os.system('unzip fastdfs-nginx-module{}.zip &&mv fastdfs-nginx-module-{}  fastdfs-nginx-module-master'.format(
                        FASTDFS_NGINX_MODULE_VERSION, FASTDFS_NGINX_MODULE_VERSION))

                    if not self.exists('fastdfs-nginx-module-master'):
                        printi('download fastdfs-nginx-module failed from github')
                        progress_bar('now download from own url', 2)
                        os.system('wget --no-check-certificate https://gitee.com/nuex/fastdfs-nginx-module/attach_files/764983/download/fastdfs-nginx-module-x.zip')
                        # 解压并重命名
                        os.system('unzip fastdfs-nginx-module-{}.zip &&mv fastdfs-nginx-module-{}  fastdfs-nginx-module-master'.format(FASTDFS_NGINX_MODULE_VERSION,FASTDFS_NGINX_MODULE_VERSION))

                        #修改.h库做软连接
                        if self.exists('fastdfs-nginx-module-master'):
                            progress_bar('modify .h path',2)
                            with open('fastdfs-nginx-module-master/src/config','r') as r:
                                content=r.read()
                            content=content.replace('ngx_module_incs="/usr/local/include"','ngx_module_incs="/usr/include/fastdfs /usr/include/fastcommon/"')
                            content=content.replace('CORE_INCS="$CORE_INCS /usr/local/include"','CORE_INCS="$CORE_INCS /usr/include/fastdfs /usr/include/fastcommon/"')
                            with open('fastdfs-nginx-module-master/src/config','w') as w:
                                w.write(content)

                #编译配置添加模块
                if os.path.exists('fastdfs-nginx-module-master'):
                    config_cmd+=' --add-module='+self.path+'nginx-'+self.version+'/fastdfs-nginx-module-master/src'
                else:
                    printi('unzip fastdfs-nginx-module-master failed')
            progress_bar('make command ...',3)
            printi(config_cmd)
            if self.exec_cmd(config_cmd):
                os.system('make && make install')
                # 更改nginx目录的拥护者
                # os.system('chown -R nginx:nginx /usr/local/nginx')
                # os.system('cp -p /usr/local/nginx/sbin/nginx /usr/sbin/nginx')
                # os.system('ln -s /usr/local/nginx/conf/nginx.conf /etc/')
                if FASTDFS_TRACKER or FASTDFS_STORAGE or FASTDFS_CLIENT:
                    if self.exists('./fastdfs-nginx-module-master/src/mod_fastdfs.conf'):
                        if not self.exists('/etc/fdfs'):
                            self.exec_cmd('mkdir -p /etc/fdfs/',0)
                        if self.exec_cmd('cp ./fastdfs-nginx-module-master/src/mod_fastdfs.conf /etc/fdfs/'):
                            mc = ModifyConfig('/etc/fdfs/mod_fastdfs.conf')
                            mc.modify_config({'connect_timeout': FASTDFS_NGINX_MODULE_CONNECT_TIMEOUT})
                            mc.modify_config({'tracker_server': FASTDFS_NGINX_MODULE_TRACKER_SERVER})
                            mc.modify_config({'url_have_group_name': FASTDFS_NGINX_MODULE_URL_HAVE_GROUP_NAME})
                            mc.modify_config({'store_path0': FASTDFS_NGINX_MODULE_STORE_PATH0})
                            mc.modify_config({'url_have_group_name': 'true'})

                        #配置nginx fastdfs模块
                        if os.path.exists(self.path+'nginx/conf/nginx.conf'):
                            with open(self.path+'nginx/conf/nginx.conf', 'r') as r:
                                content = r.read()

                            try:
                                content.index('location ~/group([0-9])/M00')#如果存在则不添加
                                printi('nginx set ngx_fast_nodule already')
                            except:
                                keyword = '        error_page   500 502 503 504  /50x.html;'
                                # print content_list
                                try:
                                    content_index = content.index(keyword)
                                    total = content[:content_index + len(keyword)] + FEED + ' '*8+content[content_index + len(
                                        keyword) + 9:]
                                    with open(self.path + 'nginx/conf/nginx.conf', 'w') as w:
                                        w.write(total)
                                except:
                                    printi('nginx.conf must has line "error_page   500 502 503 504  /50x.html;"')

            else:
                printi('\033[31mconfigure nginx failed..\033[0m')

        else:
            printi('\033[31m tar -zxf nginx-1.4.2.tar.gz failed...\033[0m')
        #清理下载和解压后的文件
        if CLEAR_RELEASE_FILE:
            os.chdir(self.path)
            os.system('rm -rf ./nginx-{}'.format(self.version))

        if CLEAR_DOWNLOAD_FILE:
            os.system('rm -rf V{}.zip'.format(FASTDFS_NGINX_MODULE_VERSION))
            os.system('rm -rf nginx-{}.tar.gz'.format(self.version))
    @property
    def download(self):
        os.chdir(self.path)
        download_url = 'http://nginx.org/download/nginx-{}.tar.gz'.format(self.version)
        download_cmd = 'wget %s' % (download_url)
        if self.exec_cmd(download_cmd):
            pass
        else:
            printi('\033[31mdownload nginx install packet  failed...\033[0m')

class I_jdk(Method):
    def __init__(self):
        pass
    def install(self):
        os.popen('rpm -qa | grep java | xargs rpm -e --nodeps')#先卸载自带的java
        os.popen('yum install java-1.8.0-openjdk* -y')#
        """export JAVA_HOME=/usr/lib/jvm/java
        export CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar:$JAVA_HOME/jre/lib/rt.jar
        export PATH=$PATH:$JAVA_HOME/bin"""#经测试不需要配置也能使用java和javac命令

class I_redis(Method):
    @property
    def download(self):
        download_url = 'http://download.redis.io/releases/redis-{}.tar.gz'.format(self.version)
        download_cmd = 'wget %s' % (download_url)
        if self.exec_cmd(download_cmd):
            pass
        else:
            printi('\033[31mdownload redis install packet  failed...\033[0m')
            sys.exit()

    @property
    def install(self):
        tar_cmd = 'tar -zxf redis-{}.tar.gz'.format(self.version)
        if self.exec_cmd(tar_cmd):
            # chroot_cmd = 'cd nginx-1.4.2 && '
            os.chdir('./redis-{}'.format(self.version))
            os.system('make && make PREFIX={}redis install'.format(self.path))#指定路径安装
            os.system('mv redis.conf {}redis/bin'.format(self.path))#将配置文件移动到bin目录下
            os.system('mkdir {}redis-cluster'.format(self.path))
            os.system('mv src/redis-trib.rb {}redis-cluster'.format(self.path))
            os.system('cd .. &&rm -rf redis-{}.tar.gz &&rm -rf redis-{}.tar.gz'.format(self.version,self.version).replace('\n',''))#删除下载的文件
            os.chdir(self.path)
            for port in REDIS_CLUSTER_PORT:#复制原redis为每个端口创建实例
                os.system('cp -r redis/bin redis-cluster/redis-{}'.format(port))
            for port in REDIS_CLUSTER_PORT:#修改每个实例的conf配置
                mrc = ModifyRedisConf('redis-cluster/redis-{}/redis.conf'.format(port))
                mrc.modify_conf('bind 127.0.0.1', 'bind '+IP)
                mrc.modify_conf('port 6379', 'port {}'.format(port))
                mrc.modify_conf('# cluster-enabled yes', 'cluster-enabled yes')
                mrc.modify_conf('# cluster-node-timeout 15000', 'cluster-node-timeout 15000')
                mrc.modify_conf('# cluster-config-file nodes-6379.conf', 'cluster-config-file nodes-{}.conf'.format(port))
                mrc.modify_conf('pidfile /var/run/redis_6379.pid', 'pidfile /var/run/redis_{}.pid'.format(port))
                mrc.modify_conf('daemonize no', 'daemonize yes')
                mrc.modify_conf('# requirepass foobared','requirepass {}'.format(REDIS_PASSWORD))
            with open('{}redis-cluster/start_all.sh'.format(self.path),'w') as w:
                content='ps auxf|grep redis |grep -v grep|xargs kill -9\n'#先杀死所有redis进程
                for port in REDIS_CLUSTER_PORT:
                    content+='./redis-{}/redis-server ./redis-{}/redis.conf'.format(port,port).replace('\n','')+'\n'
                content+='source /etc/profile.d/rvm.sh\necho 5 secends later start\nsleep 5s\n'
                content1='./redis-trib.rb create --replicas 1 '
                for port in REDIS_CLUSTER_PORT:
                    content1+=IP+':'+port+' '
                w.write(content+content1)
            os.chmod(self.path + "redis-cluster/start_all.sh",stat.S_IRWXU + stat.S_IRGRP + stat.S_IXGRP + stat.S_IROTH)#设置可执行权限：-rwxr-xr--
            #回到工作路径
            os.chdir(self.path)
            #删除残留文件
            if CLEAR_DOWNLOAD_FILE:
                os.system('rm -rf redis-{}.tar.gz'.format(self.version))
            if CLEAR_RELEASE_FILE:
                os.system('rm -rf redis-{}'.format(self.version))
        else:
            printe('\033[31m tar -zxf redis-{}.tar.gz failed...\033[0m'.format(self.version))
            sys.exit()

class I_mysql(Method):
    @property
    def download(self):
        download_url = 'http://dev.mysql.com/get/mysql57-community-release-el7-10.noarch.rpm'
        download_cmd = 'wget %s' % (download_url)
        if self.exec_cmd(download_cmd):
            pass
        else:
            printi('\033[31mdownload mysql install packet  failed...\033[0m')

    @property
    def install(self):
        rpm_cmd = 'yum -y install mysql57-community-release-el7-10.noarch.rpm'
        if self.exec_cmd(rpm_cmd):
            os.system('yum -y install mysql-community-server')
        else:
            printi('\033[31m install mysql failed...\033[0m'.format(self.version))
        if CLEAR_DOWNLOAD_FILE:
            os.system('rm -rf mysql57-community-release-el7-10.noarch.rpm')

        #卸载 需要使用rmp -e命令，查询包名：rpm -qa | grep mysql

    def get_mysql_default_pwd(self):  # 获取mysql初始化生成的密码
        file = open('/var/log/mysqld.log', 'r')
        for line in file:
            if 'A temporary password is generated for root@localhost:' in line:
                pwd_index = line.index('root@localhost: ', 0)
                pwd = line[pwd_index + 16:]
                printi('default_password:{}'.format(pwd))
                return pwd

    def set_mysql_pwd(self):
        pwd = self.get_mysql_default_pwd()
        cmd = """mysql --user=root --password={} --execute="set password for root@'localhost' = password('{}');" --connect-expired-password""".format(
            pwd, MySQL_PASSWORD).replace('\n', '')  # format方法会出自动添加现换行符
        cmd1 = """mysql --user=root --password={} --execute="set global validate_password_policy=0;" --connect-expired-password""".format(
            pwd).replace('\n', '')
        printi(cmd1)
        os.popen(cmd1)  # 设置密码复杂度
        os.popen(cmd)  # 设置密码

    def open_remote_login(self):  # 允许远程登录
        cmd = """mysql --user=root --password={} --execute="grant all privileges on *.* to 'root'@'%' identified by '{}' with grant option;flush privileges;" --connect-expired-password""".format(
            MySQL_PASSWORD, MySQL_PASSWORD).replace('\n', '')
        os.popen(cmd)

    def open_firewall(self):  # 开启3306端口
        cmd = "firewall-cmd --zone=public --add-port=3306/tcp --permanent"
        cmd1 = "firewall-cmd --reload"
        os.popen(cmd)
        os.popen(cmd1)

    @property
    def start(self):
        s_cmd='systemctl start  mysqld.service'
        st_cmd='systemctl status mysqld.service'
        os.system(s_cmd)
        os.system(st_cmd)
        self.set_mysql_pwd()
        self.open_remote_login()
        self.open_firewall()

class I_apollo(Method):
    def __init__(self,path,version, protel_ip):
        self.version=version
        self.protel_ip=protel_ip
        self.path=path
        os.chdir(self.path)
        os.system('mkdir apollo')
    @property
    def download(self):
        download_url = 'https://github.com/ctripcorp/apollo/archive/refs/tags/v{}.tar.gz'.format(self.version)
        download_cmd = 'wget %s' % (download_url)
        if self.exec_cmd(download_cmd):
            pass
        else:
            printi('\033[31mdownload apollo install packet  failed...\033[0m')

    @property
    def install(self):
        tar_cmd = 'tar -zxf v{}.tar.gz'.format(self.version)
        if self.exec_cmd(tar_cmd):
            os.chdir('./apollo-{}'.format(self.version))
        else:
            printi('\033[31m tar -zxf v{}.tar.gz failed...\033[0m'.format(self.version))
            progress_bar('now download from own url', 2)
            os.system('wget https://gitee.com/nuex/apollo/attach_files/783934/download/apollo-1.5.1.tar.gz')
            if self.exec_cmd('tar -zxvf apollo-1.5.1.tar.gz'):
                os.chdir('./apollo-1.5.1')
            else:
                printe('download apollo from own url failed')
                sys.exit()

        cmd = """mysql --user=root --password={} --execute="source ./scripts/db/migration/configdb/V1.0.0__initialization.sql" --connect-expired-password""".format(
            MySQL_PASSWORD).replace('\n', '')#执行sql初始化脚本
        cmd1="""mysql --user=root --password={} --execute="source ./scripts/db/migration/portaldb/V1.0.0__initialization.sql" --connect-expired-password""".format(
            MySQL_PASSWORD).replace('\n', '')
        os.popen(cmd)
        os.popen(cmd1)
        # 修改配置
        mc=ModifyConfig('./scripts/build.sh')
        mc.modify_config({'apollo_config_db_url':'jdbc:mysql://{}/ApolloConfigDB?useUnicode=true\&characterEncoding=utf-8\&zeroDateTimeBehavior=convertToNull\&useSSL=false\&serverTimezone=Asia/Shanghai'.format(MySQL_IP_PORT).replace('\n', ''),'apollo_config_db_username':MYSQL_USER_NAME,'apollo_config_db_password':MySQL_PASSWORD})
        mc.modify_config({'apollo_portal_db_url':'jdbc:mysql://{}/ApolloPortalDB?useUnicode=true\&characterEncoding=utf-8\&zeroDateTimeBehavior=convertToNull\&useSSL=false\&serverTimezone=Asia/Shanghai'.format(MySQL_IP_PORT).replace('\n', ''),'apollo_portal_db_username':MYSQL_USER_NAME,'apollo_portal_db_password':MySQL_PASSWORD})
        mc.modify_config({'pro_meta':APOLLO_PROTEL_IP+':8080'})
        mc.modify_config({'META_SERVERS_OPTS':'-Dpro_meta=$pro_meta'})
        mc.comment_out('dev_meta','fat_meta','uat_meta')#注释掉
        os.environ["PATH"] = "/usr/local/soft/maven/bin:" + os.environ["PATH"]
        sh.sh('-c', 'source /etc/profile')#刷新环境变量,此方法无效，子进程无法修改父进程环境
        pi=subprocess.Popen('./scripts/build.sh',shell=True,env=os.environ,stdout=subprocess.PIPE)#执行打包命令
        for line in iter(pi.stdout.readline, 'b'):
            printi(line)
            if line=='':
                break
        #接下来分别解压apollo-adminservice,apollo-configservice,apollo-portal
        pi=subprocess.Popen('unzip -o ./apollo-configservice/target/apollo-configservice-{}-github.zip -d {}apollo/apollo-configservice'.format(self.version,self.path).replace('\n', ''),shell=True,env=os.environ,stdout=subprocess.PIPE)
        for line in iter(pi.stdout.readline, 'b'):
            printi(line)
            if line=='':
                break
        pi=subprocess.Popen('unzip -o ./apollo-adminservice/target/apollo-adminservice-{}-github.zip -d {}apollo/apollo-adminservice'.format(self.version,self.path).replace('\n', ''),shell=True,env=os.environ,stdout=subprocess.PIPE)
        for line in iter(pi.stdout.readline, 'b'):
            printi(line)
            if line=='':
                break
        pi=subprocess.Popen('unzip -o ./apollo-portal/target/apollo-portal-{}-github.zip -d {}apollo/apollo-portal'.format(self.version,self.path).replace('\n', ''),shell=True,env=os.environ,stdout=subprocess.PIPE)
        for line in iter(pi.stdout.readline, 'b'):
            printi(line)
            if line=='':
                break
        if CLEAR_DOWNLOAD_FILE:
            os.chdir(INSTALL_PATH)
            os.system('rm -rf v{}.tar.gz'.format(self.version))
        if CLEAR_RELEASE_FILE:
            os.chdir(INSTALL_PATH)
            os.system('rm -rf apollo-{}'.format(self.version))

    @property
    def start(self):
        self.open_firewall(8090)
        self.open_firewall(8080)
        self.open_firewall(8070)
        mc=ModifyConfig(self.path+'apollo/apollo-portal/config/apollo-env.properties')
        mc.comment_out('dev.meta','fat.meta','uat.meta','lpt.meta')#将portal-env的注释掉
        # pi=subprocess.Popen(self.path+'apollo/apollo-adminservice/scripts/startup.sh',shell=True,env=os.environ,stdout=subprocess.PIPE)#启动脚本
        # for line in iter(pi.stdout.readline, 'b'):
        #     print line
        #     if line=='':
        #         break
        # pi=subprocess.Popen(self.path+'apollo/apollo-configservice/scripts/startup.sh',shell=True,env=os.environ,stdout=subprocess.PIPE)
        # for line in iter(pi.stdout.readline, 'b'):
        #     print line
        #     if line=='':
        #         break
        # pi=subprocess.Popen(self.path+'apollo/apollo-portal/scripts/startup.sh',shell=True,env=os.environ,stdout=subprocess.PIPE)
        # for line in iter(pi.stdout.readline, 'b'):
        #     print line
        #     if line=='':
        #         break

        printi(sh.sh('-c', self.path+'apollo/apollo-adminservice/scripts/startup.sh'))
        printi(sh.sh('-c',self.path + 'apollo/apollo-configservice/scripts/startup.sh'))
        printi(sh.sh('-c',self.path + 'apollo/apollo-portal/scripts/startup.sh'))

class I_maven(Method):
    def __init__(self, path, version):
        super(I_maven, self).__init__(path, version)
        os.chdir(self.path)
    @property
    def download(self):
        download_url = 'https://archive.apache.org/dist/maven/maven-3/{}/binaries/apache-maven-{}-bin.tar.gz'.format(MAVEN_VERSION,MAVEN_VERSION).replace('\n','')
        download_cmd = 'wget %s' % (download_url)
        if self.exec_cmd(download_cmd):
            pass
        else:
            printi('\033[31mdownload maven install packet  failed...\033[0m')

    @property
    def install(self):
        cmd = 'tar -zxf apache-maven-{}-bin.tar.gz'.format(self.version)
        if self.exec_cmd(cmd):
            os.popen('mv apache-maven-{} maven'.format(self.version))#解压后重命名
        else:
            printi('\033[31m install maven failed...\033[0m')
        with open('/etc/profile','w') as w:
            w.write("export MAVEN_HOME={}maven\nexport PATH=$MAVEN_HOME/bin:$PATH".format(self.path))#配置环境变量
        os.environ["PATH"] = "/usr/local/soft/maven/bin:" + os.environ["PATH"]
        sh.sh('-c', 'source /etc/profile')#刷新环境变量,此方法无效

        if CLEAR_DOWNLOAD_FILE:
            os.system('rm -rf apache-maven-{}-bin.tar.gz'.format(self.version))

class I_ruby(Method):
    @property
    def install(self):
        # content = ''
        # with open('/etc/hosts', 'r') as r:
        #     content = r.read()
        # content = content.replace('199.232.28.133 raw.githubusercontent.com', '')
        # with open('/etc/hosts', 'w') as w:
        #     w.write(content)
        # with open('/etc/hosts', 'a') as a:
        #     a.write('199.232.28.133 raw.githubusercontent.com')
        # os.system('gpg --keyserver 144.76.9.122 --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3')
        os.system('yum install gcc-c++ patch readline readline-devel zlib zlib-devel libyaml-devel libffi-devel openssl-devel make bzip2 autoconf automake libtool bison iconv-devel sqlite-devel')
        # os.system('curl -sSL https://rvm.io/mpapis.asc | gpg --import -')
        # os.system('curl -L get.rvm.io | bash -s stable')
        os.system('curl -sSL https://raw.github.com/wayneeseguin/rvm/master/binscripts/rvm-installer | bash')
        sp = subprocess.Popen(["/bin/bash", "-i", "-c", "source /etc/profile.d/rvm.sh &&rvm reload &&rvm requirements run &&rvm install {} &&gem install redis".format(self.version)])
        sp.communicate()
        printw('you must execute mommand: source /etc/profile.d/rvm.sh')


class I_fastdfs(Method):
    def __init__(self, path, fastdfs_version, libfastcommon_version, version=None):
        super(I_fastdfs, self).__init__(path, version)
        self.path=path
        self.fastdfs_version=fastdfs_version
        self.libfastcommon_version=libfastcommon_version
        os.chdir(self.path)
    @property
    def install(self):
        #下载并安装libfastcommon
        exec_cmd=self.exec_cmd
        progress_bar('start download libfastcommon......')
        os.system('wget --no-check-certificate https://github.com/happyfish100/libfastcommon/archive/refs/tags/V{}.zip &&unzip -o V{}.zip -d ./'.format(self.libfastcommon_version,self.libfastcommon_version).replace('\n',''))
        if not self.exists('./libfastcommon-{}'.format(self.libfastcommon_version)):
            printi('download libfastcommon failed from github')
            progress_bar('now download from own url',2)
            os.system(
                'wget --no-check-certificate https://gitee.com/nuex/libfastcommon/attach_files/764648/download/libfastcommon-1.0.7.zip &&unzip -o libfastcommon-1.0.7.zip -d ./')

            if CLEAR_DOWNLOAD_FILE:
                exec_cmd('rm -rf libfastcommon-1.0.7.zip')

        exec_cmd('cd ./libfastcommon-{} &&./make.sh && ./make.sh install'.format(self.libfastcommon_version,self.libfastcommon_version).replace('\n',''))
        #删除下载文件
        if CLEAR_DOWNLOAD_FILE:
            exec_cmd('rm -rf V{}.zip'.format(self.libfastcommon_version).replace('\n', ''))
        # 创建软连接
        exec_cmd('ln -s /usr/lib64/libfastcommon.so /usr/local/lib/libfastcommon.so')
        exec_cmd('ln -s /usr/lib64/libfastcommon.so /usr/lib/libfastcommon.so')
        exec_cmd('ln -s /usr/lib64/libfdfsclient.so /usr/local/lib/libfdfsclient.so')
        exec_cmd('ln -s /usr/lib64/libfdfsclient.so /usr/lib/libfdfsclient.so')

        #下载并安装fastdfs,弄个假进度条延迟5秒，防止github滥用检测
        progress_bar('start download fastdfs......',5)
        os.system('wget --no-check-certificate https://github.com/happyfish100/fastdfs/archive/refs/tags/V{}.zip &&unzip -o V{}.zip -d ./'.format(self.fastdfs_version,self.fastdfs_version).replace('\n',''))
        if not self.exists('./fastdfs-{}'.format(self.fastdfs_version)):
            printi('download fastdfs failed from github')
            progress_bar('now download from own url',2)
            os.system('wget --no-check-certificate https://gitee.com/nuex/fastdfs/attach_files/764624/download/fastdfs-5.05.zip &&unzip -o fastdfs-5.05.zip -d ./')
            if CLEAR_DOWNLOAD_FILE:
                exec_cmd('rm -rf fastdfs-5.05.zip')
        os.chdir(self.path)
        os.system('cd ./fastdfs-{}/ &&./make.sh &&./make.sh install'.format(self.fastdfs_version,self.fastdfs_version).replace('\n',''))

        #复制必要文件
        exec_cmd('cp ./fastdfs-{}/conf/http.conf /etc/fdfs/'.format(self.fastdfs_version).replace('\n',''))
        exec_cmd('cp ./fastdfs-{}/conf/mime.types /etc/fdfs/'.format(self.fastdfs_version).replace('\n', ''))


        # 创建软连接
        exec_cmd('ln -s /usr/bin/fdfs_trackerd /usr/local/bin')
        exec_cmd('ln -s /usr/bin/fdfs_storaged /usr/local/bin')
        exec_cmd('ln -s /usr/bin/stop.sh /usr/local/bin')
        exec_cmd('ln -s /usr/bin/restart.sh /usr/local/bin')

        #创建目录
        exec_cmd('mkdir -p {}'.format(FASTDFS_TRACKER_BASE_PATH))

        # 删除下载文件
        if CLEAR_DOWNLOAD_FILE:
            exec_cmd('rm -rf V{}.zip'.format(self.fastdfs_version).replace('\n',''))


        #配置tracker
        exec_cmd('cp /etc/fdfs/tracker.conf.sample /etc/fdfs/tracker.conf')
        mc=ModifyConfig('/etc/fdfs/tracker.conf')
        mc.modify_config({'port': FASTDFS_TRACKER_PORT})
        mc.modify_config({'base_path':FASTDFS_TRACKER_BASE_PATH})
        mc.modify_config({'http.server_por':FASTDFS_TRACKER_HTTP_SERVER_PORT})

        #防火墙打开端口
        self.open_firewall(FASTDFS_TRACKER_PORT)

        #tracker开机启动
        exec_cmd('chkconfig fdfs_trackerd on')

        #创建目录
        exec_cmd('mkdir -p {}'.format(FASTDFS_STORAGE_BASE_PATH))
        exec_cmd('mkdir -p {}'.format(FASTDFS_STORAGE_STORE_PATH0))

        #配置storage
        os.system('cp /etc/fdfs/storage.conf.sample /etc/fdfs/storage.conf')
        mc=ModifyConfig('/etc/fdfs/storage.conf')
        mc.modify_config({'base_path':FASTDFS_STORAGE_BASE_PATH})
        mc.modify_config({'http.server_port':FASTDFS_STORAGE_HTTP_SERVER_PORT})
        mc.modify_config({'store_path0': FASTDFS_STORAGE_STORE_PATH0})
        mc.modify_config({'tracker_server': FASTDFS_STORAGE_TACKER_SERVER})
        mc.modify_config({'port': FASTDFS_STORAGE_PORT})

        #防火墙打开端口
        self.open_firewall(FASTDFS_STORAGE_PORT)

        #storage开机启动
        exec_cmd('chkconfig fdfs_storaged on')

        #创建目录
        exec_cmd('mkdir -p {}'.format(FASTDFS_CLIENT_BASE_PATH))

        #配置client
        os.system('cp /etc/fdfs/client.conf.sample /etc/fdfs/client.conf')
        mc=ModifyConfig('/etc/fdfs/client.conf')
        mc.modify_config({'base_path': FASTDFS_CLIENT_BASE_PATH})
        mc.modify_config({'tracker_server':FASTDFS_CLIENT_TACKER_SERVER})

        # 删除解压的文件
        if CLEAR_RELEASE_FILE:
            exec_cmd('rm -rf fastdfs-{}'.format(self.fastdfs_version).replace('\n', ''))
            exec_cmd('rm -rf libfastcommon-{}'.format(self.libfastcommon_version).replace('\n', ''))

class I_rabbitmq(Method):
    def __init__(self,path):
        super(I_rabbitmq, self).__init__(path, version=None)
        """版本为gitee镜像库的 3.6.10"""
    @property
    def download(self):
        download_url = 'https://gitee.com/nuex/rabbitmq-server/attach_files/782808/download/rabbitmq_server-3.6.10.zip'
        download_cmd = 'wget %s' % (download_url)
        if self.exec_cmd(download_cmd):
            pass
        else:
            printi('\033[31mdownload rabbitmq packet  failed...\033[0m')

    @property
    def install(self):
        if self.exists('rabbitmq_server-3.6.10.zip'):
            #解压文件
            os.system('unzip rabbitmq_server-3.6.10.zip')
            #重命名
            os.system('mv rabbitmq_server-3.6.10  rabbitmq')
            #
            os.system("echo 'export PATH=$PATH:"+self.path+"rabbitmq/sbin' >> /etc/profile")
            #设置执行权
            os.system('chmod 777 rabbitmq/sbin/*')
            #printw('rabbit install success,but file can not execute,you should use command like: " chmod 777 rabbitmq/sbin/rabbitmq-server"')
            printw('rabbit install success,but file can not execute,you should use command like: "source /etc/profile"')
            if CLEAR_DOWNLOAD_FILE:
                os.system('rm -rf rabbitmq_server-3.6.10.zip')
        else:
            printe('rabbitmq_server-3.6.10.zip no exists')
            return 0

class I_zookeeper(Method):
    def __init__(self, path):
        super(I_zookeeper, self).__init__(path, version=None)
        """版本为mirrors.tuna.tsinghua.edu.cn 3.5.9镜像版"""
    @property
    def download(self):
        download_url = 'https://mirrors.tuna.tsinghua.edu.cn/apache/zookeeper/zookeeper-3.5.9/apache-zookeeper-3.5.9-bin.tar.gz'
        download_cmd = 'wget %s' % (download_url)
        if self.exec_cmd(download_cmd):
            pass
        else:
            printi('\033[31mdownload zookeeper packet  failed...\033[0m')

    @property
    def install(self):
        if self.exists('apache-zookeeper-3.5.9-bin.tar.gz'):
            os.system('tar -zxvf apache-zookeeper-3.5.9-bin.tar.gz')
            os.system('mv apache-zookeeper-3.5.9-bin zookeeper')
            os.system('cp zookeeper/conf/zoo_sample.cfg zookeeper/conf/zoo.cfg')
            os.system('mkdir /tmp/zookeeper')
            mc=ModifyConfig(self.path+'zookeeper/conf/zoo.cfg')
            mc.append({'admin.serverPort':2190})
            self.open_firewall(2181)
            self.open_firewall(2190)
        if CLEAR_DOWNLOAD_FILE:
            os.system('rm -rf apache-zookeeper-3.5.9-bin.tar.gz')

class I_elaseticsearch(Method):
    def __init__(self, path):
        super(I_elaseticsearch, self).__init__(path, version=None)
        """版本为官方6.8.6"""
    @property
    def download(self):
        download_url = 'https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.8.6.tar.gz'
        download_cmd = 'wget %s' % (download_url)
        if self.exec_cmd(download_cmd):
            pass
        else:
            printe('\033[31mdownload elasticsearch packet  failed...\033[0m')

    @property
    def install(self):
        if self.exists('elasticsearch-6.8.6.tar.gz'):
            os.system('tar -zxvf elasticsearch-6.8.6.tar.gz')
            os.system('mv elasticsearch-6.8.6 elasticsearch')
            self.open_firewall(9200)
            os.system('adduser {}'.format(ELASTICSEARCH_USER))
            os.system('echo {} | passwd {} --stdin'.format(ELASTICSEARCH_PWD,ELASTICSEARCH_USER).replace('\n',''))
            printi("changed {}'s password: {}".format(ELASTICSEARCH_USER,ELASTICSEARCH_PWD).replace('\n',''))
            os.system('chmod -R 777 elasticsearch/')
            mc=ModifyRedisConf(self.path+'elasticsearch/config/elasticsearch.yml')
            mc.modify_conf('#http.port: 9200','http.port: 9200')
            mc.modify_conf('#network.host: 192.168.0.1','network.host: 0.0.0.0')
            mc=ModifyRedisConf('/etc/sysctl.conf')
            mc.append('vm.max_map_count=2621441')
            mc.append('fs.file-max = 100000')
            mc=ModifyRedisConf('/etc/security/limits.conf')
            mc.append('*        hard    nofile           65536')
            mc.append('*        soft    nofile           65536')
            mc.append('*        hard    nproc  4096')
            mc.append('*        soft    nproc  4096')
            mc=ModifyRedisConf(self.path+'elasticsearch/config/jvm.options')
            mc.modify_conf('-Xms1g','-Xms512m')
            mc.modify_conf('-Xmx1g', '-Xmx512m')
            os.system('sysctl -p /etc/sysctl.conf')
        if CLEAR_DOWNLOAD_FILE:
            os.system('rm -rf elasticsearch-6.8.6.tar.gz')

class I_xxl_job(Method):
    def __init__(self, path):
        super(I_xxl_job, self).__init__(path, version=None)
        """版本为克隆gtiee 2.0.2"""
    @property
    def download(self):
        download_url = 'https://gitee.com/nuex/xxl-job/attach_files/786212/download/xxl-job-2.0.2.tar.gz'
        download_cmd = 'wget %s' % (download_url)
        if self.exec_cmd(download_cmd):
            pass
        else:
            printe('\033[31mdownload xxl-job packet  failed...\033[0m')

    @property
    def install(self):
        if self.exists('xxl-job-2.0.2.tar.gz'):
            os.system('tar -zxvf xxl-job-2.0.2.tar.gz')
            os.system('mv xxl-job-2.0.2 xxl-job')
            #创建数据库
            # os.system("""mysql --user=root --password={} --execute="create database xxl_job;" --connect-expired-password""".format(MySQL_PASSWORD).replace('\n', ''))
            #执行数据库文件
            os.system("mysql -uroot -p'zallsteel' xxl_job < xxl-job/doc/db/tables_xxl_job.sql")
            os.chdir('xxl-job')
            pi = subprocess.Popen('mvn clean package', shell=True, env=os.environ, stdout=subprocess.PIPE)
            for line in iter(pi.stdout.readline, 'b'):
                printi(line)
                if line == '':
                    break
            #修改配置文件
            mc=ModifyConfig(INSTALL_PATH+'/xxl-job/xxl-job-admin/src/main/resources/application.properties')
            mc.modify_config({'spring.datasource.url':'jdbc:mysql://{}/xxl-job?useUnicode=true\&characterEncoding=utf-8\&zeroDateTimeBehavior=convertToNull\&useSSL=false\&serverTimezone=Asia/Shanghai'.format(XXL_JOB_ADMIN_MYSQL_IP_PORT)})
            mc.modify_config({'spring.datasource.username':XXL_JOB_ADMIN_MYSQL_USER})
            mc.modify_config({'spring.datasource.password':XXL_JOB_ADMIN_MYSQL_PWD})
            #编译
            os.environ["PATH"] = INSTALL_PATH+"maven/bin:" + os.environ["PATH"]
            pi = subprocess.Popen('mvn package', shell=True, env=os.environ, stdout=subprocess.PIPE)
            for line in iter(pi.stdout.readline, 'b'):
                printi(line)
                if line == '':
                    break
            #开启端口
            self.open_firewall(8080)

            #删除下载文件
            if CLEAR_DOWNLOAD_FILE:
                os.chdir(INSTALL_PATH)
                os.system('rm -rf xxl-job-2.0.2.tar.gz')

        printw('you must modify /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.292.b10-1.el7_9.x86_64/jre/lib/security/java.security  delete SSLv3')


def set_github_host():
    gh=GitHosts()
    gh.start

def redis():
    ins = I_redis(INSTALL_PATH, REDIS_VERSION)
    ins.download
    ins.install

def mysql():
    ins=I_mysql(INSTALL_PATH,REDIS_VERSION)
    ins.download
    ins.install
    ins.start

def apollo():
    ins=I_apollo(INSTALL_PATH,APOLLO_VERSION,APOLLO_PROTEL_IP)
    ins.download
    ins.install
    ins.start

def maven():
    ins=I_maven(INSTALL_PATH,MAVEN_VERSION)
    ins.download
    ins.install

def ruby():
    ins=I_ruby(INSTALL_PATH,RUBY_VERSION)
    ins.install

def nginx():
    ins=I_nginx(INSTALL_PATH,NGINX_VERSION)
    ins.download
    ins.install

def fastdfs():
    ins=I_fastdfs(INSTALL_PATH,FASTDFS_VERSION,LIBFASTCOMMON_VERSION)
    ins.install

def rabbitmq():
    ins=I_rabbitmq(INSTALL_PATH)
    ins.download
    ins.install

def java():
    ins=I_jdk()
    ins.install()

def xxl_job_admin():
    ins=I_xxl_job(INSTALL_PATH)
    ins.download
    ins.install


def zookeeper():
    ins=I_zookeeper(INSTALL_PATH)
    ins.download
    ins.install

def elasticsearch():
    ins=I_elaseticsearch(INSTALL_PATH)
    ins.download
    ins.install


'./configure --with-http_stub_status_module --with-http_ssl_module --with-http_gzip_static_module --with-http_flv_module --add-module=/usr/local/soft/nginx-1.2.1/fastdfs-nginx-module-master/src'

def init():
    #设置时区
    printi('start set timezone Asia/Shanghai')
    os.system('timedatectl set-timezone Asia/Shanghai')

    #安装依赖
    printi('start Install dependencies')
    printi(ENV_TOOL_LIST)
    # os.system('yum -y install gcc wget automake autoconf unzip libtool make gcc-c++ pcre* zlib* openssl openssl-devel libevent erlang')
    cmd='yum -y install '
    for x in ENV_TOOL_LIST:
        cmd+=(x+' ')
    cmd.strip()
    os.system(cmd)
    #爬取并设置github ip地址
    printi('start crawl github host')
    progress_bar('start github spider......',3)
    set_github_host()
    #创建路径
    printi('start create directory {}'.format(INSTALL_PATH))
    os.system('mkdir {}'.format(INSTALL_PATH))



FUNC_MAP_LIST = [{'java': JAVA}, {'ruby': RUBY}, {'maven': MAVEN}, {'nginx': NGINX}, {'zookeeper': ZOOKEEPER},
                  {'mysql': MYSQL}, {'apollo': APOLLO}, {'xxl_job_admin': XXL_JOB_ADMIN},
                 {'redis': REDIS}, {'rabbitmq': RABBITMQ}, {'elasticsearch': ELASTICSEARCH}]

ENV_TOOL_LIST = ['gcc-4.8.5-44.el7.x86_64', 'wget-1.14-18.el7_6.1.x86_64', 'automake-1.13.4-3.el7.noarch',
                    'autoconf-2.69-11.el7.noarch', 'unzip-6.0-22.el7_9.x86_64', 'libtool-2.4.2-22.el7_3.x86_64',
                    'make-3.82-24.el7.x86_64', 'gcc-c++-4.8.5-44.el7.x86_64', 'pcre-8.32-17.el7.x86_64',
                    'pcre-devel-8.32-17.el7.x86_64', 'pcre-tools-8.32-17.el7.x86_64', 'pcre2-tools-10.23-2.el7.x86_64',
                    'pcre2-utf16-10.23-2.el7.x86_64', 'pcre2-static-10.23-2.el7.x86_64',
                    'pcre-static-8.32-17.el7.x86_64', 'pcre2-10.23-2.el7.x86_64', 'pcre2-devel-10.23-2.el7.x86_64',
                    'pcre2-utf32-10.23-2.el7.x86_64', 'zlib-devel-1.2.7-19.el7_9.x86_64',
                    'zlib-static-1.2.7-19.el7_9.x86_64', 'zlib-1.2.7-19.el7_9.x86_64',
                    'zlib-ada-1.4-0.5.20120830CVS.el7.x86_64', 'zlib-ada-devel-1.4-0.5.20120830CVS.el7.x86_64',
                    'openssl-1.0.2k-21.el7_9.x86_64', 'openssl-devel-1.0.2k-21.el7_9.x86_64',
                    'libevent-2.0.21-4.el7.x86_64', 'erlang-R16B-03.18.el7.x86_64']




if __name__ == '__main__':
    init()
    fm=FUNC_MAP(FUNC_MAP_LIST)
    fm.execute()













