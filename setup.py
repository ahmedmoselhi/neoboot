from __future__ import print_function
from distutils.core import setup
import os


PLUGIN_DIR = 'Extensions.NeoBoot'


def compile_translate():
    for lang in os.listdir('po'):
        if lang.endswith('.po'):
            src = os.path.join('po', lang)
            lang = lang[:-3]
            destdir = os.path.join('src/locale', lang, 'LC_MESSAGES')
            if not os.path.exists(destdir):
                os.makedirs(destdir)
            dest = os.path.join(destdir, 'NeoBoot.mo')
            print("Language compile %s -> %s" % (src, dest))
            if os.system("msgfmt '%s' -o '%s'" % (src, dest)) != 0:
                raise RuntimeError("Failed to compile", src)


compile_translate()


setup(
    name='enigma2-plugin-extensions-neoboot',
    version='1.0',
    author='gutosie / ahmedmoselhi',
    author_email='ahmedmoselhi55@gmail.com',
    package_dir={
        PLUGIN_DIR: 'src'},
    packages=[PLUGIN_DIR],
    package_data={
        PLUGIN_DIR: [
            '*.png',
            '*.mvi',
            '*.cfg',
            'bin/*',
            'files/*',
            'neoskins/*.ttf',
            'neoskins/biko/*.png',
            'neoskins/biko2/*.png',
            'neoskins/cobaltfhd/*.png',
            'neoskins/darog69/*.png',
            'neoskins/darog69_Ustym4kpro/*.png',
            'neoskins/metrix/skin/*.png',
            'neoskins/nitro/skin/*.png',
            'images/*.png',
            'ubi_reader_arm/ubifs/*.so',
            'ubi_reader_mips/ubifs/*.so',
            'locale/*/LC_MESSAGES/*.mo']},
    description='Install Multiple enigma2 images on flash usb')
