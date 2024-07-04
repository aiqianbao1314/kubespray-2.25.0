import os
import sys
from urllib.parse import urlparse
from subprocess import getstatusoutput
import multiprocessing


def create_directory(path):
    try:
        os.makedirs(path)
        # print(f"Successfully created directory: {path}")
        create_result = 0
    except FileExistsError:
        # print(f"Directory already exists: {path}")
        create_result = 1
    except Exception as e:
        print(f"An error occurred while creating directory: {path}")
        print(e)
        return None


def download_file():
    with open('temp/files.list') as f:
        os.system('rm -rf k8s-pak')
        for url in f:
            print(url)
            parsed_url = urlparse(url)
            save_path = f'k8s-pak/{parsed_url.hostname}/{"/".join(parsed_url.path.split("/")[0:-1])}'
            create_directory(save_path)
            proxies = {
                'http': 'http://192.168.110.132:7890',
                'https': 'http://192.168.110.132:7890'
            }
            os.environ['http_proxy'] = proxies['http']
            os.environ['https_proxy'] = proxies['http']
            os.system('wget -P ' + save_path + ' ' + url)


def pull_image(image):
    pull_cmd = f'docker pull  {image}'
    res = getstatusoutput(pull_cmd)
    if res[0] > 0:
        print(f'下载失败: {pull_cmd}')
    else:
        print(f'下载成功: {pull_cmd}')


# 批量下载镜像,docker需要手动配置代理,并打包
def docker_pull_image():
    pool = multiprocessing.Pool(5)
    with open('temp/images.list') as f:
        for image in f:
            pool.apply_async(pull_image, args=(image.strip(),))
        pool.close()
        pool.join()
    # os.system('docker save -o images.tar $(cat temp/images.list | xargs) ')


if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == 'file':
            download_file()
        elif sys.argv[1] == 'image':
            docker_pull_image()
    else:
        download_file()
        docker_pull_image()
