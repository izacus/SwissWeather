from setuptools import setup, Extension

setup(name="SwissWeather",
      version="1.0.0",
      description="A client to retrieve current weather and forecast from Swiss MeteoSwiss service.",      
      license="GPLv2+",
      author="Jernej Virag",
      author_email="jernej@virag.si",      
      install_requires = ["requests==2.28.1"],
      classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
      ],            
      packages=["swiss-weather"])