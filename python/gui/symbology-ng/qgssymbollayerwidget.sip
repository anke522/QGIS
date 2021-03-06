class QgsSymbolLayerWidget : QWidget
{
%TypeHeaderCode
#include <qgssymbollayerwidget.h>
%End

  public:
    QgsSymbolLayerWidget( QWidget *parent /TransferThis/, const QgsVectorLayer *vl = 0 );
    virtual ~QgsSymbolLayerWidget();

    virtual void setSymbolLayer( QgsSymbolLayer *layer ) = 0;
    virtual QgsSymbolLayer *symbolLayer() = 0;

    /** Sets the context in which the symbol widget is shown, e.g., the associated map canvas and expression contexts.
     * @param context symbol widget context
     * @see context()
     * @note added in QGIS 3.0
     */
    void setContext( const QgsSymbolWidgetContext &context );

    /** Returns the context in which the symbol widget is shown, e.g., the associated map canvas and expression contexts.
     * @see setContext()
     * @note added in QGIS 3.0
     */
    QgsSymbolWidgetContext context() const;

    /** Returns the vector layer associated with the widget.
     * @note added in QGIS 2.12
     */
    const QgsVectorLayer *vectorLayer() const;

  protected:
    void registerDataDefinedButton( QgsPropertyOverrideButton *button, QgsSymbolLayer::Property key );

    QgsExpressionContext createExpressionContext() const;

  signals:
    /**
     * Should be emitted whenever configuration changes happened on this symbol layer configuration.
     * If the subsymbol is changed, {@link symbolChanged()} should be emitted instead.
     */
    void changed();
    /**
     * Should be emitted whenever the sub symbol changed on this symbol layer configuration.
     * Normally {@link changed()} should be preferred.
     *
     * @see {@link changed()}
     */
    void symbolChanged();

  protected slots:
    void updateDataDefinedProperty();
};

///////////

class QgsSimpleLineSymbolLayerWidget : QgsSymbolLayerWidget
{
%TypeHeaderCode
#include <qgssymbollayerwidget.h>
%End

  public:
    QgsSimpleLineSymbolLayerWidget( const QgsVectorLayer *vl, QWidget *parent /TransferThis/ = NULL );

    static QgsSymbolLayerWidget *create( const QgsVectorLayer *vl ) /Factory/;

    // from base class
    virtual void setSymbolLayer( QgsSymbolLayer *layer );
    virtual QgsSymbolLayer *symbolLayer();

  public slots:
    void penWidthChanged();
    void colorChanged( const QColor &color );
    void penStyleChanged();
    void offsetChanged();
    void on_mCustomCheckBox_stateChanged( int state );
    void on_mChangePatternButton_clicked();
    void on_mPenWidthUnitWidget_changed();
    void on_mOffsetUnitWidget_changed();
    void on_mDashPatternUnitWidget_changed();
    void on_mDrawInsideCheckBox_stateChanged( int state );

  protected:
    //creates a new icon for the 'change pattern' button
    void updatePatternIcon();
};

///////////

class QgsSimpleMarkerSymbolLayerWidget : QgsSymbolLayerWidget
{
%TypeHeaderCode
#include <qgssymbollayerwidget.h>
%End

  public:
    QgsSimpleMarkerSymbolLayerWidget( const QgsVectorLayer *vl, QWidget *parent /TransferThis/ = NULL );
    ~QgsSimpleMarkerSymbolLayerWidget();

    static QgsSymbolLayerWidget *create( const QgsVectorLayer *vl ) /Factory/;

    // from base class
    virtual void setSymbolLayer( QgsSymbolLayer *layer );
    virtual QgsSymbolLayer *symbolLayer();

  public slots:
    void setColorStroke( const QColor &color );
    void setColorFill( const QColor &color );
    void setSize();
    void setAngle();
    void setOffset();
    void on_mSizeUnitWidget_changed();
    void on_mOffsetUnitWidget_changed();
    void on_mStrokeWidthUnitWidget_changed();
    void on_mStrokeStyleComboBox_currentIndexChanged( int index );
    void on_mStrokeWidthSpinBox_valueChanged( double d );
    void on_mHorizontalAnchorComboBox_currentIndexChanged( int index );
    void on_mVerticalAnchorComboBox_currentIndexChanged( int index );
};

///////////

class QgsSimpleFillSymbolLayerWidget : QgsSymbolLayerWidget
{
%TypeHeaderCode
#include <qgssymbollayerwidget.h>
%End

  public:
    QgsSimpleFillSymbolLayerWidget( const QgsVectorLayer *vl, QWidget *parent /TransferThis/ = NULL );

    static QgsSymbolLayerWidget *create( const QgsVectorLayer *vl ) /Factory/;

    // from base class
    virtual void setSymbolLayer( QgsSymbolLayer *layer );
    virtual QgsSymbolLayer *symbolLayer();

  public slots:
    void setColor( const QColor &color );
    void setStrokeColor( const QColor &color );
    void setBrushStyle();
    void strokeWidthChanged();
    void strokeStyleChanged();
    void offsetChanged();
    void on_mStrokeWidthUnitWidget_changed();
    void on_mOffsetUnitWidget_changed();
};


///////////

/** \ingroup gui
 * \class QgsFilledMarkerSymbolLayerWidget
 * \brief Widget for configuring QgsFilledMarkerSymbolLayer symbol layers.
 * \note Added in version 2.16
 */
class QgsFilledMarkerSymbolLayerWidget : QgsSymbolLayerWidget
{
%TypeHeaderCode
#include <qgssymbollayerwidget.h>
%End

  public:

    /** Constructor for QgsFilledMarkerSymbolLayerWidget.
     * @param vl associated vector layer
     * @param parent parent widget
     */
    QgsFilledMarkerSymbolLayerWidget( const QgsVectorLayer *vl, QWidget *parent /TransferThis/ = nullptr );

    ~QgsFilledMarkerSymbolLayerWidget();

    /** Creates a new QgsFilledMarkerSymbolLayerWidget.
     * @param vl associated vector layer
     */
    static QgsSymbolLayerWidget *create( const QgsVectorLayer *vl ) /Factory/;

    // from base class
    virtual void setSymbolLayer( QgsSymbolLayer *layer );
    virtual QgsSymbolLayer *symbolLayer();

};

///////////


class QgsGradientFillSymbolLayerWidget : QgsSymbolLayerWidget
{
%TypeHeaderCode
#include <qgssymbollayerwidget.h>
%End
  public:
    QgsGradientFillSymbolLayerWidget( const QgsVectorLayer *vl, QWidget *parent /TransferThis/ = NULL );

    static QgsSymbolLayerWidget *create( const QgsVectorLayer *vl ) /Factory/;

    // from base class
    virtual void setSymbolLayer( QgsSymbolLayer *layer );
    virtual QgsSymbolLayer *symbolLayer();

  public slots:
    void setColor( const QColor &color );
    void setColor2( const QColor &color );
    void applyColorRamp();
    void setGradientType( int index );
    void setCoordinateMode( int index );
    void setGradientSpread( int index );
    void offsetChanged();
    void referencePointChanged();
    void on_mOffsetUnitWidget_changed();
    void colorModeChanged();
    void on_mSpinAngle_valueChanged( double value );
};

///////////

class QgsShapeburstFillSymbolLayerWidget : QgsSymbolLayerWidget
{
%TypeHeaderCode
#include <qgssymbollayerwidget.h>
%End
  public:
    QgsShapeburstFillSymbolLayerWidget( const QgsVectorLayer *vl, QWidget *parent /TransferThis/ = NULL );

    static QgsSymbolLayerWidget *create( const QgsVectorLayer *vl ) /Factory/;

    // from base class
    virtual void setSymbolLayer( QgsSymbolLayer *layer );
    virtual QgsSymbolLayer *symbolLayer();

  public slots:
    void setColor( const QColor &color );
    void setColor2( const QColor &color );
    void colorModeChanged();
    void on_mSpinBlurRadius_valueChanged( int value );
    void on_mSpinMaxDistance_valueChanged( double value );
    void on_mDistanceUnitWidget_changed();
    void on_mRadioUseWholeShape_toggled( bool value );
    void applyColorRamp();
    void offsetChanged();
    void on_mOffsetUnitWidget_changed();
    void on_mIgnoreRingsCheckBox_stateChanged( int state );
};

///////////

class QgsMarkerLineSymbolLayerWidget : QgsSymbolLayerWidget
{
%TypeHeaderCode
#include <qgssymbollayerwidget.h>
%End
  public:
    QgsMarkerLineSymbolLayerWidget( const QgsVectorLayer *vl, QWidget *parent /TransferThis/ = NULL );

    static QgsSymbolLayerWidget *create( const QgsVectorLayer *vl ) /Factory/;

    // from base class
    virtual void setSymbolLayer( QgsSymbolLayer *layer );
    virtual QgsSymbolLayer *symbolLayer();

  public slots:

    void setInterval( double val );
    void setOffsetAlongLine( double val );
    void setRotate();
    void setOffset();
    void setPlacement();
    void on_mIntervalUnitWidget_changed();
    void on_mOffsetUnitWidget_changed();
    void on_mOffsetAlongLineUnitWidget_changed();
};


///////////

class QgsSvgMarkerSymbolLayerWidget : QgsSymbolLayerWidget
{
%TypeHeaderCode
#include <qgssymbollayerwidget.h>
%End

  public:
    QgsSvgMarkerSymbolLayerWidget( const QgsVectorLayer *vl, QWidget *parent /TransferThis/ = NULL );
    ~QgsSvgMarkerSymbolLayerWidget();

    static QgsSymbolLayerWidget *create( const QgsVectorLayer *vl ) /Factory/;

    // from base class
    virtual void setSymbolLayer( QgsSymbolLayer *layer );
    virtual QgsSymbolLayer *symbolLayer();

  public slots:
    void setName( const QModelIndex &idx );
    void populateIcons( const QModelIndex &idx );
    void setSize();
    void setAngle();
    void setOffset();
    void on_mFileToolButton_clicked();
    void on_mFileLineEdit_textEdited( const QString &text );
    void on_mFileLineEdit_editingFinished();
    void on_mChangeColorButton_colorChanged( const QColor &color );
    void on_mChangeStrokeColorButton_colorChanged( const QColor &color );
    void on_mStrokeWidthSpinBox_valueChanged( double d );
    void on_mSizeUnitWidget_changed();
    void on_mStrokeWidthUnitWidget_changed();
    void on_mOffsetUnitWidget_changed();
    void on_mHorizontalAnchorComboBox_currentIndexChanged( int index );
    void on_mVerticalAnchorComboBox_currentIndexChanged( int index );

  protected:

    void populateList();
    //update gui for svg file (insert new path, update activation of gui elements for svg params)
    void setGuiForSvg( const QgsSvgMarkerSymbolLayer *layer );
};

///////////

class QgsRasterFillSymbolLayerWidget : QgsSymbolLayerWidget
{
%TypeHeaderCode
#include <qgssymbollayerwidget.h>
%End

  public:
    QgsRasterFillSymbolLayerWidget( const QgsVectorLayer *vl, QWidget *parent /TransferThis/ = NULL );

    static QgsSymbolLayerWidget *create( const QgsVectorLayer *vl ) /Factory/;

    // from base class
    virtual void setSymbolLayer( QgsSymbolLayer *layer );
    virtual QgsSymbolLayer *symbolLayer();

};

///////////

class QgsSVGFillSymbolLayerWidget : QgsSymbolLayerWidget
{
%TypeHeaderCode
#include <qgssymbollayerwidget.h>
%End

  public:
    QgsSVGFillSymbolLayerWidget( const QgsVectorLayer *vl, QWidget *parent /TransferThis/ = NULL );

    static QgsSymbolLayerWidget *create( const QgsVectorLayer *vl ) /Factory/;

    // from base class
    virtual void setSymbolLayer( QgsSymbolLayer *layer );
    virtual QgsSymbolLayer *symbolLayer();

  protected:
    void insertIcons();
    /** Enables or disables svg fill color, stroke color and stroke width based on whether the
     * svg file supports custom parameters.
     * @param resetValues set to true to overwrite existing layer fill color, stroke color and stroke width
     * with default values from svg file
     */
    void updateParamGui( bool resetValues = true );
};

//////////

class QgsLinePatternFillSymbolLayerWidget : QgsSymbolLayerWidget
{
%TypeHeaderCode
#include <qgssymbollayerwidget.h>
%End
  public:

    QgsLinePatternFillSymbolLayerWidget( const QgsVectorLayer *vl, QWidget *parent /TransferThis/ = NULL );
    static QgsSymbolLayerWidget *create( const QgsVectorLayer *vl ) /Factory/;

    virtual void setSymbolLayer( QgsSymbolLayer *layer );
    virtual QgsSymbolLayer *symbolLayer();
};

//////////

class QgsPointPatternFillSymbolLayerWidget: QgsSymbolLayerWidget
{
%TypeHeaderCode
#include <qgssymbollayerwidget.h>
%End

  public:
    QgsPointPatternFillSymbolLayerWidget( const QgsVectorLayer *vl, QWidget *parent /TransferThis/ = NULL );
    static QgsSymbolLayerWidget *create( const QgsVectorLayer *vl ) /Factory/;

    virtual void setSymbolLayer( QgsSymbolLayer *layer );
    virtual QgsSymbolLayer *symbolLayer();
};

/////////

class QgsFontMarkerSymbolLayerWidget : QgsSymbolLayerWidget
{
%TypeHeaderCode
#include <qgssymbollayerwidget.h>
%End

  public:
    QgsFontMarkerSymbolLayerWidget( const QgsVectorLayer *vl, QWidget *parent /TransferThis/ = NULL );

    ~QgsFontMarkerSymbolLayerWidget();

    static QgsSymbolLayerWidget *create( const QgsVectorLayer *vl ) /Factory/;

    // from base class
    virtual void setSymbolLayer( QgsSymbolLayer *layer );
    virtual QgsSymbolLayer *symbolLayer();

  public slots:
    void setFontFamily( const QFont &font );
    void setColor( const QColor &color );

    /** Set stroke color.
     * @note added in 2.16 */
    void setColorStroke( const QColor &color );
    void setSize( double size );
    void setAngle( double angle );
    void setCharacter( QChar chr );
    void setOffset();
    void on_mSizeUnitWidget_changed();
    void on_mOffsetUnitWidget_changed();
    void on_mStrokeWidthUnitWidget_changed();
    void on_mStrokeWidthSpinBox_valueChanged( double d );
    void on_mHorizontalAnchorComboBox_currentIndexChanged( int index );
    void on_mVerticalAnchorComboBox_currentIndexChanged( int index );
};

//////////

class QgsCentroidFillSymbolLayerWidget : QgsSymbolLayerWidget
{
%TypeHeaderCode
#include <qgssymbollayerwidget.h>
%End

  public:
    QgsCentroidFillSymbolLayerWidget( const QgsVectorLayer *vl, QWidget *parent /TransferThis/ = NULL );

    static QgsSymbolLayerWidget *create( const QgsVectorLayer *vl ) /Factory/;

    // from base class
    virtual void setSymbolLayer( QgsSymbolLayer *layer );
    virtual QgsSymbolLayer *symbolLayer();
};


class QgsGeometryGeneratorSymbolLayerWidget : QgsSymbolLayerWidget
{
%TypeHeaderCode
#include <qgssymbollayerwidget.h>
%End
  public:
    QgsGeometryGeneratorSymbolLayerWidget( const QgsVectorLayer *vl, QWidget *parent /TransferThis/ = nullptr );

    /**
     * Will be registered as factory
     */
    static QgsSymbolLayerWidget *create( const QgsVectorLayer *vl ) /Factory/;

    // from base class
    virtual void setSymbolLayer( QgsSymbolLayer *layer );
    virtual QgsSymbolLayer *symbolLayer();
};
