/*
Copyright (C) 2025, Oak Ridge National Laboratory
Copyright (C) 2021, Anand Seethepalli and Larry York
Copyright (C) 2020, Courtesy of Noble Research Institute, LLC

File: main.cpp

Authors:
Anand Seethepalli (seethepallia@ornl.gov)
Larry York (yorklm@ornl.gov)

This file is part of RhizoVision Explorer.

RhizoVision Explorer is free software: you can redistribute
it and/or modify it under the terms of the GNU General Public
License as published by the Free Software Foundation, either
version 3 of the License, or (at your option) any later version.

RhizoVision Explorer is distributed in the hope that it will
be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public
License along with RhizoVision Explorer; see the file COPYING.
If not, see <https://www.gnu.org/licenses/>.
*/

#include <QtWidgets/QApplication>
#include <QtWidgets/QMessageBox>

#include "MainUI.h"

#include "feature_extraction.h"

using namespace std;
using namespace cv;
using namespace cvutil;

//#ifdef NDEBUG
//#define DEBUG_MODE
//#endif

int main(int argc, char *argv[])
{
    setUseOptimized(true);
    
    if (!checkHardwareSupport(CV_CPU_AVX2))
    {
        init(argc, argv, false);
        setUseOptimized(false);
    }
    else
    {
        init(argc, argv, true);
    }

    //QApplication::setAttribute(Qt::AA_EnableHighDpiScaling);

    QCoreApplication *app = QApplication::instance();
    app->setApplicationName("RhizoVision Explorer");

    Ptr<cvutilWindow> wnd = getImageProcessorWindow(QIcon(":/icons/RVElogoclearback.png"));
    wnd->enableROI(true);
    wnd->setVisibleROI(true);
    wnd->enableActions(true);
    wnd->setVisibleActions(true);
    wnd->setInitialBanner(QPixmap(":/icons/RVElogoclearback.png").scaledToHeight(200, Qt::SmoothTransformation),
        QPixmap(), // QPixmap(":/icons/noble-logo-color.png").scaledToHeight(50, Qt::SmoothTransformation),
        "RhizoVision Explorer (v" RHIZOVISION_EXPLORER_VERSION ")",
        "Load a plant root image from File menu\n             or drag and drop it here.");
    MainUI *dialog = new MainUI();
    dialog->setprocessfunction(feature_extractor);
    dialog->setHostWindow(wnd.get());
    
    QObject::connect(dialog, &MainUI::updateVisualOutput, [&](Mat m) { wnd->setImage(m); });
    //QObject::connect(dialog, &MainUI::updateProgress, [&](QString status) { wnd->updateProgress(status); });
    
    if (dialog == nullptr)
    {
        std::cerr << "Failed to create main dialog." << std::endl;
        return -1;
    }
    
    if (wnd == nullptr)
    {
        std::cerr << "Failed to create image processor window." << std::endl;
        return -1;
    }
    
    wnd->loadPlugins(dialog);
    wnd->show();
    
    try
    {
        return QApplication::exec();
    }
    catch (const std::exception &e)
    {
        QMessageBox::critical(nullptr, "Error", QString("An error occurred: %1").arg(e.what()));
        return -1;
    }
    catch (...)
    {
        QMessageBox::critical(nullptr, "Error", "An unknown error occurred.");
        return -1;
    }
}
