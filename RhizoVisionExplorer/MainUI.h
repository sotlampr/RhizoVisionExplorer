/*
Copyright (C) 2025, Oak Ridge National Laboratory
Copyright (C) 2021, Anand Seethepalli and Larry York
Copyright (C) 2020, Courtesy of Noble Research Institute, LLC

File: MainUI.h

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

// Generate MOC code using the following command
// moc --include C:\Path\to\PluginInterfaces.h MainUI.h -o moc_MainUI.cpp

#pragma once

#ifndef MAINUI_H
#define MAINUI_H

#include <string>
#include <filesystem>

#include <QtWidgets/QDialog>
#include <QtWidgets/QtWidgets>
#include <QtCore/QQueue>
#include <QtCore/QElapsedTimer>

#include <cvutil.h>
#include <PluginManager.h>
#include <RoiManager.h>

//#include "FeatureExtractorThread.h"

QT_BEGIN_NAMESPACE
class QAction;
class QDialogButtonBox;
class QGroupBox;
class QLabel;
class QLineEdit;
class QMenu;
class QMenuBar;
class QPushButton;
class QTextEdit;
class QCheckBox;
class QProgressBar;
class QVBoxLayout;
class QStatusBar;
class QSpinBox;
class QDoubleSpinBox;
class QSlider;
class QComboBox;
QT_END_NAMESPACE

#include "feature_config.h"

class CheckEnabler : public QWidget
{
    Q_OBJECT;

private:
    QCheckBox *cb;
    QLineEdit *edt;
    QLabel *lbl;

    QHBoxLayout *layout;
    std::vector<QWidget *> widgets;

public:
    CheckEnabler(QString text, QString lbl, bool integervalue = false, QWidget *parent = nullptr);

    bool checked() const { return cb->isChecked(); };
    void setChecked(bool on) { cb->setChecked(on); };
    double getValue() const { return edt->text().toDouble(); };
    void setValue(double val) { edt->setText(QString::number(val, 'g')); };
    void setValue(QString val) { edt->setText(val); };
    void setLabelText(QString text) { lbl->setText(text); };

    void addToLayout(QWidget *w) { layout->addWidget(w, 0, Qt::AlignLeft); widgets.push_back(w); this->update(); }
    //void setWhatsThis(const QString &msg) { QWidget::setWhatsThis(msg); }

signals:
    void stateChanged();
    void textChanged();
};

class StringCheckEnabler : public QWidget
{
    Q_OBJECT;

private:
    QCheckBox *cb;
    QLineEdit *edt;
    QLabel *lbl;

public:
    StringCheckEnabler(QString text, QString lbl, QWidget *parent = nullptr);

    bool checked() const { return cb->isChecked(); };
    void setChecked(bool on) { cb->setChecked(on); };
    QString getValue() const { return edt->text(); };
    void setValue(QString val) { edt->setText(val); };

    //void setWhatsThis(const QString &msg) { QWidget::setWhatsThis(msg); }

signals:
    void stateChanged();
    void textChanged();
};

class MainUI : public QObject, public IPlugin
{
    Q_OBJECT;
    Q_INTERFACES(IPlugin);
    Q_PLUGIN_METADATA(IID IPlugin_iid FILE "RhizoVisionExplorer.json");

public:
    typedef void(*processfunc)(feature_config* config);
    
    MainUI();
    //~MainUI();
    void setprocessfunction(processfunc pfunc);
    void setHostWindow(cvutil::cvutilWindow *wnd);
    
//private:
    //MainUI(std::shared_ptr<feature_config> fconfig);
public slots:
    std::string getName();
    AppType getApplicationType();
    OutputType getOutputType();
    std::string getAlgorithmName();
    std::vector<IParameterInfo *> getParameters();
    QWidget *getPluginUI();
    void setImage(cv::Mat image, QString imagename = "");
    void execute();
    std::vector<cv::Mat> getOutputImages();
    int getDisplayIndex();
    void setDisplayIndex(int idx);
    std::vector<double> getFeatures();
    std::vector<double> getFeatures(int roiidx);
    void setBatchMode(bool on);
    int saveOutput(QString savloc, QString inputfilename);
    void saveMetadata(QString imgloc, QString savloc, QString filepath = "");
    void loadMetadata(QString filepath);
    int writeHeader(QString savloc, QString filename = "");
    std::vector<QString> getCSVColumnNames();
    int getProgressSteps();
    void abort();
    QChart *getChart();

signals:
    void updateVisualOutput(cv::Mat m);
    void updateProgress(QString status);

private:
    void createOptions();
    void createRangeControls();
    void updateRangeControls();
    void enablepixelconversion();
    void connectSignalstoSlots();
    //void enableinvertimage();
    //void enablesavesegmented();
    //void enablesaveprocessed();
    void updateconversion();
    void setTextWhatsThis();
    void spboxvaluechanged(QDoubleSpinBox *s, double k);
    void addrangerowclicked(double lastdrange = -1.0f);
    void removerangerowclicked();
    void colorizechart(QChart *chart, int size);

private slots:
    void updatesegmentedoutput();

private:
    QVBoxLayout *vlayout;
    QLabel *lbroottype, *lbdispoutput;
    QComboBox *roottype, *dispoutput, *pixelspermm;
    //QCheckBox *invertimage; //, *savesegmented, *saveprocessed; // , *convertunits;
    //QCheckBox *enableRootPruning;
    QPushButton *pbpreview;
    cv::Ptr<figure> f;
    QIcon rightarrow, downarrow;

    bool dispoutputupdating = false;
    bool executing = false; // Gaurd to prevent thread unsafe way to update config->displayOutputIndex.
    std::vector<double> drangeview; // To synchronize diameter range view (UI) and the internal list (config->drange).
    
    StringCheckEnabler *saveseg, *savepro;
    CheckEnabler *convertunits, *linesmooth, *filterbknoisy, *filterfgnoisy, *enableRootPruning;
    QLabel *ranges;
    QLineEdit *featurefileedt, *metadatafileedt;
    QCheckBox *keepLargest;

    std::vector<QLabel *> dranges;
    std::vector<QLineEdit *> editmins;
    std::vector<QDoubleSpinBox *> spboxes;
    QPushButton *addrangerow, *removerangerow;

    QLabel* thresh;
    QSlider *thresholdslider;
    QSpinBox *thresholdbox;
    QProgressBar *thresholdbar;

    QCheckBox *showConvexHull, *showHoles; // For whole root only
    QCheckBox *showDistMap, *showMedialAxisDiameter;
    CheckEnabler *showMedialAxis, *showContours;
    
    //int roottypeval = 0;
    std::shared_ptr<feature_config> config;
    processfunc pfunc;

    cvutilWindow* hostWindow = nullptr;
    QScrollArea *pluginuiarea = nullptr;
    QToolBox *pluginui = nullptr;
};

#endif // DIALOG_H

