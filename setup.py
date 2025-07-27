from setuptools import setup, Extension

setup(name="SwissWeather",
      version="1.2.1",
      description="A client to retrieve current weather and forecast from Swiss MeteoSwiss service.",      
      license="GPLv2+",
      author="Jernej Virag",
      author_email="jernej@virag.si",      
      setup_requires=['pytest-runner==5.3.1'],
      install_requires = ["requests==2.28.1"],
      tests_require = ["responses==0.13.3", "pytest==7.1.2"],
      classifiers=[
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
      ],            
      packages=["swissweather"],
      test_suite="tests")