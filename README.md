# RenovMemo - Implementasi Perangkat Lunak

> Tugas Besar - IF2150 Rekayasa Perangkat Lunak

<div align="center">
  <p align="center">
    <h2>RenovMemo</h2>
<br>
</p>
</div>
<div align="center" id="contributor">
  <strong>
    <h3>Dipersiapkan oleh K-03 G-06</h3>
    <table align="center">
      <tr>
        <td style="text-align: center;">NIM</td>
        <td style="text-align: center;">Nama</td>
      </tr>
      <tr>
        <td style="text-align: center;">13523126</td>
        <td style="text-align: center;">Brian Ricardo Tamin</td>
      </tr>
      <tr>
        <td style="text-align: center;">13523141</td>
        <td style="text-align: center;">Jovandra Otniel P.S.</td>
      </tr>
      <tr>
        <td style="text-align: center;">13523142</td>
        <td style="text-align: center;">Nathanael Rachmat</td>
      </tr>
      <tr>
        <td style="text-align: center;">13523148</td>
        <td style="text-align: center;">Andrew Tedjapratama</td>
      </tr>
      <tr>
        <td style="text-align: center;">13523154</td>
        <td style="text-align: center;">Theo Kurniady</td>
      </tr>
    </table>
  </strong>
</div>

## **Project Setup Instructions**

Follow these steps to set up and run the project locally:

### **Prerequisites**

-   Ensure you have Python 3.8 or later installed.
-   Install `pip`, the Python package manager (comes pre-installed with Python 3.4+).

---

### **Setup Steps**

1. **Clone the Repository**
   First, clone the project repository:

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Create a Virtual Environment**
   Create a virtual environment in the project directory:

    ```bash
    python -m venv .venv
    ```

3. **Activate the Virtual Environment**
   Activate the virtual environment:

    - **Windows**:
        ```bash
        .venv\Scripts\activate
        ```
    - **Mac/Linux**:
        ```bash
        source .venv/bin/activate
        ```

4. **Install Project Dependencies**
   Install the required Python dependencies listed in `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

5. **Run the Application**
   Run the application:
    ```bash
    python src/main.py
    ```

---

### **Important Notes**

-   Always activate the virtual environment before running the project to ensure you use the correct dependencies.
-   If additional dependencies are required, install them in the virtual environment and update `requirements.txt`:
    ```bash
    pip freeze > requirements.txt
    ```

---

### **Troubleshooting**

1. **Missing Python or Pip**:

    - Ensure Python is installed and accessible in your system's PATH. Check Python version:
        ```bash
        python --version
        ```
    - Check Pip version:
        ```bash
        pip --version
        ```

2. **Virtual Environment Issues**:
   If the virtual environment is not activating, ensure you are using the correct activation command for your operating system.

3. **Dependency Installation Issues**:
   If a dependency fails to install, verify compatibility with your Python version and operating system.

4. **Flet Module Not Recognized After Installing Requirements**:
   If you encounter the following error:
    ```
    Traceback (most recent call last):
      File "src/main.py", line 2, in <module>
        import flet as ft
    ModuleNotFoundError: No module named 'flet'
    ```
    Run the following commands after activating your virtual environment:
    ```bash
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    pip install -r requirements.txt
    python src/main.py
    ```
