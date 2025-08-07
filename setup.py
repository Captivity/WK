from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dting",
    version="1.0.0",
    author="DTing Team",
    author_email="dting@example.com",
    description="DTing - Real-time collection tool for Android/iOS performance data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dting-team/DTing",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Monitoring",
        "Topic :: Mobile",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.0.0",
        "flask-socketio>=5.0.0",
        "psutil>=5.8.0",
        "matplotlib>=3.5.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "requests>=2.25.0",
        "selenium>=4.0.0",
        "pymobiledevice3>=1.0.0",
        "adb-shell>=0.4.0",
        "websockets>=10.0",
        "Pillow>=8.0.0",
        "plotly>=5.0.0",
        "dash>=2.0.0",
        "python-socketio>=5.0.0",
        "eventlet>=0.33.0",
    ],
    entry_points={
        "console_scripts": [
            "dting=dting.main:main",
            "dting-server=dting.server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "dting": [
            "templates/*.html",
            "static/css/*.css",
            "static/js/*.js",
            "static/images/*",
        ],
    },
)