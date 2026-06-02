from setuptools import setup, find_packages
setup(
    name="meeting-summary",
    version="1.0.0",
    description="Teams meeting transcript AI analysis tool",
    py_modules=["run","meeting_analyzer","transcript_parser"],
    install_requires=["httpx>=0.27.0"],
    python_requires=">=3.8",
    entry_points={"console_scripts": ["meeting-summary=run:main"]},
)