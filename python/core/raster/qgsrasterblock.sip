class QgsRasterBlock
{
%TypeHeaderCode
#include <qgis.h>
#include <qgsrasterblock.h>
%End

  public:
    QgsRasterBlock();

    /** \brief Constructor which allocates data block in memory
     *  @param dataType raster data type
     *  @param width width of data matrix
     *  @param height height of data matrix
     */
    QgsRasterBlock( Qgis::DataType dataType, int width, int height );

    virtual ~QgsRasterBlock();

    /** \brief Reset block
     *  @param dataType raster data type
     *  @param width width of data matrix
     *  @param height height of data matrix
     *  @return true on success
     */
    bool reset( Qgis::DataType dataType, int width, int height );

    // TODO: consider if use isValid() at all, isEmpty() should be sufficient
    // and works also if block is valid but empty - difference between valid and empty?
    /** \brief Returns true if the block is valid (correctly filled with data).
     *  An empty block may still be valid (if zero size block was requested).
     *  If the block is not valid, error may be retrieved by error() method.
     */
    bool isValid() const;

    /** \brief Mark block as valid or invalid */
    void setValid( bool valid );

    /** Returns true if block is empty, i.e. its size is 0 (zero rows or cols).
     *  This method does not return true if size is not zero and all values are
     *  'no data' (null).
     */
    bool isEmpty() const;

    // Return data type size in bytes
    static int typeSize( int dataType );

    // Data type in bytes
    int dataTypeSize() const;

    /** Returns true if data type is numeric */
    static bool typeIsNumeric( Qgis::DataType type );

    /** Returns true if data type is color */
    static bool typeIsColor( Qgis::DataType type );

    /** Returns data type */
    Qgis::DataType dataType() const;

    /** For given data type returns wider type and sets no data value */
    static Qgis::DataType typeWithNoDataValue( Qgis::DataType dataType, double *noDataValue );

    /** True if the block has no data value.
     * @return true if the block has no data value
     * @see noDataValue(), setNoDataValue(), resetNoDataValue()
     */
    bool hasNoDataValue() const;

    /** Returns true if the block may contain no data. It does not guarantee
     * that it really contains any no data. It can be used to speed up processing.
     * Not the difference between this method and hasNoDataValue().
     * @return true if the block may contain no data */
    bool hasNoData() const;

    /** Sets cell value that will be considered as "no data".
     * @note added in QGIS 3.0
     * @see noDataValue(), hasNoDataValue(), resetNoDataValue()
     */
    void setNoDataValue( double noDataValue );

    /** Reset no data value: if there was a no data value previously set,
     * it will be discarded.
     * @note added in QGIS 3.0
     * @see noDataValue(), hasNoDataValue(), setNoDataValue()
     */
    void resetNoDataValue();

    /** Return no data value. If the block does not have a no data value the
     *  returned value is undefined.
     * @return No data value
     * @see hasNoDataValue(), setNoDataValue(), resetNoDataValue()
     */
    double noDataValue() const;

    /** Get byte array representing a value.
     * @param dataType data type
     * @param value value
     * @return byte array representing the value */
    static QByteArray valueBytes( Qgis::DataType dataType, double value );

    /** \brief Read a single value if type of block is numeric. If type is color,
     *  returned value is undefined.
     *  @param row row index
     *  @param column column index
     *  @return value */
    double value( int row, int column ) const;

    /** \brief Read a single value if type of block is numeric. If type is color,
     *  returned value is undefined.
     *  @param index data matrix index (long type in Python)
     *  @return value */
    double value( qgssize index ) const;

    /** \brief Read a single color
     *  @param row row index
     *  @param column column index
     *  @return color */
    QRgb color( int row, int column ) const;

    /** \brief Read a single value
     *  @param index data matrix index (long type in Python)
     *  @return color */
    QRgb color( qgssize index ) const;

    /** \brief Check if value at position is no data
     *  @param row row index
     *  @param column column index
     *  @return true if value is no data */
    bool isNoData( int row, int column );

    /** \brief Check if value at position is no data
     *  @param index data matrix index (long type in Python)
     *  @return true if value is no data */
    bool isNoData( qgssize index );

    /** \brief Set value on position
     *  @param row row index
     *  @param column column index
     *  @param value the value to be set
     *  @return true on success */
    bool setValue( int row, int column, double value );

    /** \brief Set value on index (indexed line by line)
     *  @param index data matrix index (long type in Python)
     *  @param value the value to be set
     *  @return true on success */
    bool setValue( qgssize index, double value );

    /** \brief Set color on position
     *  @param row row index
     *  @param column column index
     *  @param color the color to be set, QRgb value
     *  @return true on success */
    bool setColor( int row, int column, QRgb color );

    /** \brief Set color on index (indexed line by line)
     *  @param index data matrix index (long type in Python)
     *  @param color the color to be set, QRgb value
     *  @return true on success */
    bool setColor( qgssize index, QRgb color );

    /** \brief Set no data on pixel
     *  @param row row index
     *  @param column column index
     *  @return true on success */
    bool setIsNoData( int row, int column );

    /** \brief Set no data on pixel
     *  @param index data matrix index (long type in Python)
     *  @return true on success */
    bool setIsNoData( qgssize index );

    /** \brief Set the whole block to no data
     *  @return true on success */
    bool setIsNoData();

    /** \brief Set the whole block to no data except specified rectangle
     *  @return true on success */
    bool setIsNoDataExcept( QRect exceptRect );

    /** \brief Remove no data flag on pixel. If the raster block does not have an explicit
     * no data value set then an internal map of no data pixels is maintained for the block.
     * In this case it is possible to reset a pixel to flag it as having valid data using this
     * method. This method has no effect for raster blocks with an explicit no data value set.
     *  @param row row index
     *  @param column column index
     *  @note added in QGIS 2.10 */
    void setIsData( int row, int column );

    /** \brief Remove no data flag on pixel. If the raster block does not have an explicit
     * no data value set then an internal map of no data pixels is maintained for the block.
     * In this case it is possible to reset a pixel to flag it as having valid data using this
     * method. This method has no effect for raster blocks with an explicit no data value set.
     *  @param index data matrix index (long type in Python)
     *  @note added in QGIS 2.10 */
    void setIsData( qgssize index );

    /** Get access to raw data.
     * The returned QByteArray instance is not a copy of the data: it only refers to the array
     * owned by the QgsRasterBlock, therefore it is only valid while the QgsRasterBlock object
     * still exists. Writing to the returned QByteArray will not affect the original data:
     * a deep copy of the data will be made and only the local copy will be modified.
     * @note in Python the method returns ordinary bytes object as the
     * @note added in QGIS 3.0
     */
    QByteArray data() const;

    /** Rewrite raw pixel data.
     * If the data array is shorter than the internal array within the raster block object,
     * pixels at the end will stay untouched. If the data array is longer than the internal
     * array, only the initial data from the input array will be used.
     * Optionally it is possible to set non-zero offset (in bytes) if the input data should
     * overwrite data somewhere in the middle of the internal buffer.
     * @note added in QGIS 3.0
     */
    void setData( const QByteArray &data, int offset = 0 );

    /** \brief Get pointer to data
     *  @param row row index
     *  @param column column index
     *  @return pointer to data
     */
     void *bits( int row, int column ) /PyName=bitsByRowCol/ [char * ()];

    /** \brief Get pointer to data
     *  @param index data matrix index (long type in Python)
     *  @return pointer to data
     */
     void *bits( qgssize index ) /PyName=bitsByIndex/ [char * ()];

    /** \brief Get pointer to data
     *  @return pointer to data
     *  @note not available in python bindings
     */
     void *bits() [char * ()];

    /** \brief Print double value with all necessary significant digits.
     *         It is ensured that conversion back to double gives the same number.
     *  @param value the value to be printed
     *  @return string representing the value*/
    static QString printValue( double value );

    /** \brief Convert data to different type.
     *  @param destDataType dest data type
     *  @return true on success */
    bool convert( Qgis::DataType destDataType );

    /** \brief Get image if type is color.
    *   @return image */
    QImage image() const;

    /** \brief set image.
     *  @param image image
     *  @return true on success */
    bool setImage( const QImage  *image );

    // @note not available in python bindings
    // inline static double readValue( void *data, Qgis::DataType type, qgssize index );

    // @note not available in python bindings
    // inline static void writeValue( void *data, Qgis::DataType type, qgssize index, double value );

    void applyNoDataValues( const QgsRasterRangeList  &rangeList );

    /** Apply band scale and offset to raster block values
     * @@note added in 2.3 */
    void applyScaleOffset( double scale, double offset );

    /** \brief Get error */
    QgsError error() const;

    /** \brief Set error */
    void setError( const QgsError  &error );

    QString toString() const;

    /** \brief For extent and width, height find rectangle covered by subextent.
     * The output rect has x oriented from left to right and y from top to bottom
     * (upper-left to lower-right orientation).
     * @param extent extent, usually the larger
     * @param width numbers of columns in theExtent
     * @param height numbers of rows in theExtent
     * @param subExtent extent, usually smaller than theExtent
     * @return the rectangle covered by sub extent
     */
    static QRect subRect( const QgsRectangle &extent, int width, int height, const QgsRectangle &subExtent );

    /** Returns the width (number of columns) of the raster block.
     * @see height
     * @note added in QGIS 2.10
     */
    int width() const;

    /** Returns the height (number of rows) of the raster block.
     * @see width
     * @note added in QGIS 2.10
     */
    int height() const;
};

