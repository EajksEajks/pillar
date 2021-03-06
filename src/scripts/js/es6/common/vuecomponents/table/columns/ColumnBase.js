import { CellDefault } from '../cells/renderer/CellDefault'

/**
 * Column logic
 */

export class ColumnBase {
    constructor(displayName, columnType) {
        this.displayName = displayName;
        this.columnType = columnType;
        this.isMandatory = false;
        this.includedByDefault = true;
        this.isSortable = true;
        this.isHighLighted = 0;
    }

    /**
     * 
     * @param {RowObject} rowObject 
     * @returns {String} Name of the Cell renderer component
     */
    getCellRenderer(rowObject) {
        return CellDefault.options.name;
    }

    /**
     * 
     * @param {RowObject} rowObject 
     * @returns {*} Raw unformated value
     */
    getRawCellValue(rowObject) {
        // Should be overridden
        throw Error('Not implemented');
    }

    /**
     * Cell tooltip
     * @param {Any} rawCellValue 
     * @param {RowObject} rowObject 
     * @returns {String}
     */
    getCellTitle(rawCellValue, rowObject) {
        // Should be overridden
        return '';
    }

    /**
     * Object with css classes to use on the column
     * @returns {Object} Object with css classes
     */
    getColumnClasses() {
        // Should be overridden
        let classes = {}
        classes[this.columnType] = true;
        return classes;
    }

    /**
     * Object with css classes to use on the header cell
     * @returns {Object} Object with css classes
     */
    getHeaderCellClasses() {
        // Should be overridden
        return this.getColumnClasses();
    }

    /**
     * Object with css classes to use on the cell
     * @param {*} rawCellValue 
     * @param {*} rowObject 
     * @returns {Any} Object with css classes
     */
    getCellClasses(rawCellValue, rowObject) {
        // Should be overridden
        let classes = this.getColumnClasses();
        classes['highlight'] = !!this.isHighLighted;
        return classes;
    }

    /**
     * Compare  two rows to sort them. Can be overridden for more complex situations.
     * 
     * @param {RowObject} rowObject1 
     * @param {RowObject} rowObject2 
     * @returns {Number} -1, 0, 1
     */
    compareRows(rowObject1, rowObject2) {
        let rawCellValue1 = this.getRawCellValue(rowObject1);
        let rawCellValue2 = this.getRawCellValue(rowObject2);
        if (rawCellValue1 === rawCellValue2) return 0;
        return rawCellValue1 < rawCellValue2 ? -1 : 1;
    }

    /**
     * 
     * @param {Boolean}
     */
    highlightColumn(value) {
        this.isHighLighted += !!value ? 1 : -1;
    }
}
