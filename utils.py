# coding:utf-8
# @author:nuex,http://handsome.ink
# for centos7 x64  mini install
import os,sys,time,commands
try:
    from bs4 import BeautifulSoup
    import requests
except:
    os.system('yum -y install epel-release')
    os.system('yum -y install python-pip')
    os.system('pip install bs4')
    os.system('pip install requests')
    try:
        from bs4 import BeautifulSoup
        import requests
    except:
        print 'import bs4 or requests module failed'
class ModifyConfig(object):
    def __init__(self, file_name):
        """
        :param file_name: 完整的路径和文件名
        """
        self.file_name = file_name

    def modify_config(self, kwargs):
        """
        :param file_name:完整的路径和文件名
        :param kwargs: 加入文本显示的第一行是a=b第二行是c=d 则传入参数应为{'a':'f','c':'f'}
        文本中 a和b必须唯一
        :return: 无返回值 结果是文本中的a变成f，c变成f
        """

        need_modify_items = []  # params:index,value

        with open(self.file_name, 'r') as r:
            content = r.readlines()

        for line in range(len(content)):
            for key, value in kwargs.items():
                if key + '=' in content[line] and (content[line][:len(key) + 1] == key + '='):  # key=必须在行首
                    need_modify_items.append([line, key + '=' + value])

        for item in need_modify_items:
            content[item[0]] = item[1] + '\n'  # 每行需要加换行符
        final_contant = ''
        for line in content:
            final_contant += line
        # print final_contant
        with open(self.file_name, 'w') as w:
            w.write(final_contant)

    def comment_out(self, *args):
        """

        :param keys:key list
        :return:
        """
        need_replace = []
        with open(self.file_name, 'r') as r:
            content = r.readlines()

        for line in range(len(content)):
            for key in args:
                if key + '=' in content[line] and (content[line][:len(key) + 1] == key + '='):
                    need_replace.append(content[line])
        print need_replace
        with open(self.file_name, 'r') as w:
            final_content = w.read()

        for need in need_replace:
            final_content = final_content.replace(need, '#' + need)

        with open(self.file_name, 'w') as w:
            w.write(final_content)

    def append(self,kwargs):
        """

        :param kwargs:添加的字段，如果字段已存在文本中，则不会添加
        :return:
        """
        need_append_items={}
        for key,value in kwargs.items():
            need_append_items[key]=[value,1]

        with open(self.file_name, 'r') as r:
            content=r.readlines()

        for line in range(len(content)):#先检查是否存在已key，如果存在则不能添加，因为会发生不可预期的错误
            for key, value in kwargs.items():
                if key+'='in content[line] and (content[line][:len(key)+1]==key+'='):#key=必须在行首
                    print 'key:{}'.format(key),'is exist can not append it'
                    need_append_items[key]=[value,0]
        with open(self.file_name, 'a') as a:
            for key, value in need_append_items.items():
                if value[1] == 1:
                    a.write(key+'='+str(value[0])+'\n')

    def get_items(self):
        pass



conf_path = "/usr/local/soft/redis/bin/redis.conf"  # 配置文件路径

class ModifyRedisConf(object):
    def __init__(self,name):
        self.name=name

    def modify_conf(self,old,new):
        """

        :param old: 'bind 127.0.0.1'
        :param new: '#bind 127.0.0.1'
        :return:
        """

        with open(self.name,'r') as r:
            source_content=r.readlines()
        final_content_list=source_content
        final_content=''
        index_point=0
        for line in range(len(source_content)):
            if source_content[line]==old+'\n':
                final_content_list[line]=new
                print 'find item:',source_content[line]
                index_point=line
                break
        if not '\n' in final_content_list[index_point]:
            final_content_list[index_point]+='\n'

        for line in final_content_list:
            final_content+=line
        with open(self.name,'w') as w:
            w.write(final_content)


    def append(self,content):
        with open(self.name,'r') as r:
            source_content=r.readlines()
        content_index=-1
        #存在则不动，不存在则添加
        try:
            content_index=source_content.index(content)
            # source_content[content_index]=content
            # final_content=''
            # for line in source_content:
            #     final_content+=line
            #
            # with open(self.name,'w') as w:
            #     w.write(final_content)
            print content, 'exists'

        except:
            final_content = ''
            for line in source_content:
                final_content += line
            if '\n' not in source_content[-1]:
                final_content=final_content+'\n'+content
            else:
                final_content+=content
            with open(self.name, 'w') as w:
                w.write(final_content)



class GitHosts:
    def __init__(self,filename=None):
        if filename==None:
            self.filename='/etc/hosts'
        else:
            self.filename=filename
        self.ip_list =[]
        self.header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
        self.ip_1 = 'https://github.com.ipaddress.com/' # github.com
        self.ip_2 = 'https://github.com.ipaddress.com/gist.github.com' # gist.github.com
        self.ip_3 = 'https://github.com.ipaddress.com/assets-cdn.github.com' # assets-cdn.github.com
        self.ip_4 = 'https://githubusercontent.com.ipaddress.com/raw.githubusercontent.com' # raw.githubusercontent.com
    def get_1(self): # github.com
        response = requests.get(self.ip_1, headers = self.header)
        soup = BeautifulSoup(response.text, features='lxml')
        # print(soup.find_all('ul', {'class': 'comma-separated'})[0].text + '    github.com')
        self.ip_list.append(soup.find_all('ul', {'class': 'comma-separated'})[0].text.encode('utf-8') + '    github.com')
    def get_2(self):
        response = requests.get(self.ip_2, headers = self.header)
        soup = BeautifulSoup(response.text, features = 'lxml')
        # print(soup.find_all('ul', {'class': 'comma-separated'})[0].text + '    gist.github.com')
        self.ip_list.append(soup.find_all('ul', {'class': 'comma-separated'})[0].text.encode('utf-8') + '    gist.github.com')
    def get_3(self):
        response = requests.get(self.ip_3, headers = self.header)
        soup = BeautifulSoup(response.text, features = 'lxml')
        ips = soup.find_all('li')
        for i in range(4):
            # print(ips[i].text + '    assets-cdn.github.com')
            self.ip_list.append(ips[i].text.encode('utf-8') + '    assets-cdn.github.com')
    def get_4(self):
        response = requests.get(self.ip_4, headers = self.header)
        soup = BeautifulSoup(response.text, features = 'lxml')
        # print(soup.find_all('a', {'target': '_blank'})[26].text + '    raw.githubusercontent.com')
        ip = soup.find('tbody', {'id': 'dnsinfo'}).find('tr').find_all('td')[2].find('a').text.encode('utf-8')
        self.ip_list.append(ip + '    raw.githubusercontent.com')
        self.ip_list.append(ip + '    gist.githubusercontent.com')
        self.ip_list.append(ip + '    cloud.githubusercontent.com')
        self.ip_list.append(ip + '    camo.githubusercontent.com')
        self.ip_list.append(ip + '    avatars0.githubusercontent.com')
        self.ip_list.append(ip + '    avatars1.githubusercontent.com')
        self.ip_list.append(ip + '    avatars2.githubusercontent.com')
        self.ip_list.append(ip + '    avatars3.githubusercontent.com')
        self.ip_list.append(ip + '    avatars4.githubusercontent.com')
        self.ip_list.append(ip + '    avatars5.githubusercontent.com')
        self.ip_list.append(ip + '    avatars6.githubusercontent.com')
        self.ip_list.append(ip + '    avatars7.githubusercontent.com')
        self.ip_list.append(ip + '    avatars8.githubusercontent.com')
    def set_hosts(self):
        domain_names=['github.com', 'gist.github.com', 'assets-cdn.github.com', 'assets-cdn.github.com', 'assets-cdn.github.com', 'assets-cdn.github.com', 'raw.githubusercontent.com', 'gist.githubusercontent.com', 'cloud.githubusercontent.com', 'camo.githubusercontent.com', 'avatars0.githubusercontent.com', 'avatars1.githubusercontent.com', 'avatars2.githubusercontent.com', 'avatars3.githubusercontent.com', 'avatars4.githubusercontent.com', 'avatars5.githubusercontent.com', 'avatars6.githubusercontent.com', 'avatars7.githubusercontent.com', 'avatars8.githubusercontent.com']
        content_list=[]
        content=''
        with open(self.filename,'r') as r:
            source_list =r.readlines()
        #过滤掉需要替换的字段
        ok=1
        for line in source_list:
            for domain_name in domain_names:
                try:
                    if line[line.index(domain_name):]==domain_name+'\n':
                        print 'field exists:' + line[line.index(domain_name):]
                        ok=0
                        break
                    else:
                        continue
                except:
                    continue
            if ok==1:
                content_list.append(line)
        if '\n' not in content_list[-1]:
            content_list[-1] += '\n'
        content_list+=[ip+'\n' for ip in self.ip_list]
        for line in content_list:
            content+=line
        with open(self.filename,'w') as w:
            w.write(content)

    def restart_network(self):
        os.system('/etc/init.d/network restart')
    @property
    def start(self):
        error=0
        try:
            self.get_1()
        except :
            print('github.com error')
            error += 1
        try:
            self.get_2()
        except:
            print('gist.github.com error')
            error += 1
        try:
            self.get_3()
        except:
            print('assets-cdn.github.com error')
            error += 1
        try:
            self.get_4()
        except:
            print('raw.githubusercontent.com error')
            error += 1
        # print(github.ip_list)
        if error == 0:
            for i in self.ip_list:
                print(i)
            self.set_hosts()
            self.restart_network()

def progress_bar(display_text=None,delay=None):
    if display_text==None:
        display_text='please wait...'
    if delay==None:
        delay=5.0
    else:
        delay=float(delay)
    print display_text
    for i in range(11):
        if i != 10:
            sys.stdout.write("==")
        else:
            sys.stdout.write("== " + str(i * 10) + "%/100%")
        sys.stdout.flush()
        time.sleep(delay/10)
    print ''
if __name__ == '__main__':
    # mrc=ModifyRedisConf('redis.conf')
    # mrc.modify_conf('bind 127.0.0.1','#bind 127.0.0.1')
    # import stat
    # os.chmod(INSTALL_PATH+"redis-cluster/start_all.sh", stat.S_IRWXU + stat.S_IRGRP + stat.S_IXGRP + stat.S_IROTH)
    # os.system('chmod -x {}redis-cluster/start_all.sh'.format(INSTALL_PATH))
    pass

    # os.system('curl -sSL https://raw.github.com/wayneeseguin/rvm/master/binscripts/rvm-installer | bash')
    # os.system('yum install gcc-c++ patch readline readline-devel zlib zlib-devel libyaml-devel libffi-devel openssl-devel make bzip2 autoconf automake libtool bison iconv-devel sqlite-devel')
    # sp = subprocess.Popen(["/bin/bash", "-i", "-c", "source /etc/profile &&rvm"])
    # sp.communicate()

    class A:
        def __init__(self):
            print 123
    print __file__[:-3].split('/')[-1]