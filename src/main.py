import sys
from PyQt5.QtWidgets import QApplication
from HomeScreen import HomeScreen
from product_rate_calculator import ProductRateCalculatorApp

def main():
    app = QApplication(sys.argv)
    window = HomeScreen()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
