-- Query to extract open purchase orders
#Old Query
SELECT  pha.po_header_id
,       pla.po_line_id
,	    pha.segment1                PO_NUMBER            
,       pla.line_num                po_line
,       pla.quantity
,       pla.unit_meas_lookup_code   uom
,       sup.vendor_name             supplier
,       msb.segment1                item
,       msb.description             item_desc
,       msb.inventory_item_id       item_id
,       pll.shipment_num            po_shipment_line
FROM    po_headers_all          pha
JOIN    po_lines_all            pla ON  pla.po_header_id            = pha.po_header_id
JOIN    po_line_locations_all   pll ON  pll.po_line_id              = pla.po_line_id
JOIN    ap_suppliers            sup ON  sup.vendor_id               = pha.vendor_id
JOIN    mtl_system_items_b      msb ON  msb.inventory_item_id       = pla.item_id
                                    AND msb.organization_id         = pll.ship_to_organization_id
WHERE   NVL(pha.closed_code,'OPEN') = 'OPEN'

#New Query
SELECT pha.po_header_id
, pha.attribute15
, pla.po_line_id
, pha.segment1 PO_NUMBER
, pla.line_num po_line
, pll.quantity
, pla.unit_meas_lookup_code uom
, sup.vendor_name supplier
, msb.segment1 item
, msb.description item_desc
, msb.inventory_item_id item_id
, pll.shipment_num po_shipment_line
FROM po_headers_all pha
JOIN po_lines_all pla ON pla.po_header_id = pha.po_header_id
JOIN po_line_locations_all pll ON pll.po_line_id = pla.po_line_id
JOIN ap_suppliers sup ON sup.vendor_id = pha.vendor_id
JOIN mtl_system_items_b msb ON msb.inventory_item_id = pla.item_id
AND msb.organization_id = pll.ship_to_organization_id
WHERE NVL(pll.closed_code,'OPEN') = 'OPEN'
AND pha.authorization_status = 'APPROVED' AND (pha.attribute15 = 'N' OR pha.attribute15 is NULL)

O/P:
{'PO_HEADER_ID': 48013, 'PO_LINE_ID': 50100, 'PO_NUMBER': '400496', 'PO_LINE': 1, 'QUANTITY': 5000, 
'UOM': 'Kilogram', 'SUPPLIER': 'San Miguel Mills, Inc.', 'ITEM': 'FD01A', 'ITEM_DESC': 'Flour', 
'ITEM_ID': 287, 'PO_SHIPMENT_LINE': 1},
-----------------------------------------------------------------------------------------------------------

-- Query product information

SELECT  organization_id
,       inventory_item_id
,       segment1
,       description
FROM    mtl_system_items_b  msb

/* mtl_system_items_b is the main table for inventory item information used on purchase orders.
   segment1 column is the product code or short name and the description column describes the 
   item. organization_id and inventory_item_id combined is the unique identifier/primary key of
   the table.
*/
O/P:
{'ORGANIZATION_ID': 123, 'INVENTORY_ITEM_ID': 261012, 'SEGMENT1': 'TRK-1273A',
 'DESCRIPTION': 'Chocolate Streussel Mix; 25 kg/bag'}
-----------------------------------------------------------------------------------------------------------

-- Query to get vendor information

SELECT  vendor_id
,       vendor_name
FROM    ap_suppliers

/* ap_suppliers is the table for vendor information. vendor_id is the unique identifier/primary key
   of the table. Although vendor_id is the unique identifier, vendor_name is also unique (at least for
   the current client).
*/
O/P:
{'VENDOR_ID': 325039, 'VENDOR_NAME': 'Jepy L. Pajarillo'}
-----------------------------------------------------------------------------------------------------------

-- Query to get purchase order information

SELECT  pha.po_header_id
,       pla.po_line_id
,       pha.segment1		    po_number
,		pla.line_num
,		pha.vendor_id
,       pha.closed_code
,       pha.closed_date
,       pla.item_id		    item
,       pla.item_description	    item_desc
,       pla.unit_meas_lookup_code  uom
,       pla.quantity
,       pla.closed_code
FROM    po_headers_all  pha
JOIN    po_lines_all    pla ON  pla.po_header_id   = pha.po_header_id

/* Purchase order information uses 2 tables. One is po_headers_all that stores main information like
   - po_header_id			- unique identifier/primary key of the table
   - segment1				- purchase order number column
   - vendor_id				- foreign key for table ap_suppliers
   - closed_code			- indicate if the purchase order is open or not ("OPEN" for open purchase orders
							and "CLOSED" and "FINALLY CLOSED" for closed purchase orders. There may be a 
							chance that this column is null but it can also means that the purchase order
							is open.)
   - closed_date			- another indicator if the purchase order is open or closed. If this column is
							null then it means that the purchase order is still open for the time that it
							is queried. But closed_code is enough for now.
   The other table, po_lines_all stores information of the items in every purchase order like
   - po_line_id				- unique identifier/primary key of the table
   - po_header_id			- foreign key for table po_headers_all
   - line_num				- column to identify lines for front end users
   - item_id				- foreign key for table mtl_system_items_b
   - item_description		- although this table contains the foreign key for mtl_system_items_b, it also
							stores item description which is mostly equivalent to column description of
							mtl_system_items_b.
   - unit_meas_lookup_code	- column for unit of measure for the item (eg. Kilogram, Pack, etc.)
   - quantity				- column for the quantity of the item included in the purchase order
   - closed_code			- po_lines_all also has a column that indicates if it is open or closed. Usually
							if the header is closed for the line, line is also closed. But closed_code column
							of po_headers_all is enough for now.
*/
O/P: 
{'PO_HEADER_ID': 1461805, 'PO_LINE_ID': 1574664, 'SEGMENT1': '250003962', 'LINE_NUM': 3, 
'VENDOR_ID': 270038, 'CLOSED_CODE': 'OPEN', 'CLOSED_DATE': None, 'ITEM_ID': None,
 'ITEM_DESCRIPTION': 'Bond Paper Long  s-20, Paper one', 'UNIT_MEAS_LOOKUP_CODE': 'Ream', 'QUANTITY': 4}

{'PO_HEADER_ID': 9, 'PO_LINE_ID': 16, 'PO_NUMBER': '400009', 'LINE_NUM': 1, 'VENDOR_ID': 2030, 
'CLOSED_CODE': 'CLOSED', 'CLOSED_DATE': datetime.datetime(2016, 4, 14, 15, 5, 15), 'ITEM': None, 
'ITEM_DESC': 'Fabrication and Installation of G.I. Goose Neck', 'UOM': 'Lot', 'QUANTITY': 1}
-----------------------------------------------------------------------------------------------------------

-- Insert script to populate interface table 

/* There are 2 interface tables where information should be populated to receive a purchase order. Note that
   there is still a program to be run for the PO receipt to totally imported.
   
   Also, those tables contains more column than specified here, but those columns specified here are enough
   to process receipt of a purchase order.
   
   Note also that I may not explain well some columns and why I input that value there but it is all that it
   needs to work.
*/

-- The first one is:

INSERT INTO rcv_headers_interface
	(header_interface_id
	/* header_interface_id: this is a unique identifier for rcv_headers_interface table. Although the value
	   entered here will not be carried or pass to other table when importing, it is strongly recommended to
	   use the existing database sequence rcv_headers_interface_s so the entered row will be unique and will
	   also not interrupt other future insert on this table.
	*/
	,group_id
	/* group_id: this column is used as a grouping identifier on what are included on a batch. This is a
	   parameter when running the import program so that not everything on the table will be processed. Same
	   with header_interface_id, the value will also not be carried or pass to other table when importing but
	   it is still strongly recommended to use the existing database sequence rcv_interface_groups_s (this
	   sequence is different from the sequence use by header_interface_id) so batch will be unique and will
	   also not interrupt other future insert on this table.
	*/
	,processing_status_code
	/* processing_status_code: column to identify what should be process by the import program. It is also
	   updated by the said program when error happens or the import is successful and finished. Use "PENDING"
	   value so row can be picked up by the said program.
	*/
	,receipt_source_code
	/* receipt_source_code: I am not sure what this is for but mostly of po receiving has a "VENDOR" value
	   for this.
	*/
	,transaction_type
	/* transaction_type: I am not sure about this but use "NEW" for now. It might also contain some value that
	   means updating an existing PO receipt but I am not sure. I will research for this further if needed.
	*/
	,last_update_date
	/* last_update_date: this is just 1 of the standard column of Oracle for every table. It notes when was a
	   certain row has been updated recently. You can use the current time (time when the insert script run) or
	   just use the function "SYSDATE" of Oracle to get the current date and time to fill the value.
	*/
	,last_updated_by
	/* last_updated_by: this is another 1 of the standard column of Oracle for every table. It notes who is the
	   user that did the recent update on a row. You can use 0 (zero) for now.
	*/
	,last_update_login
	/* last_update_login: I am not sure about this but I think it will be same with last_updated_by. Just use 0 (zero)
	   on this for now.
	*/
	,vendor_id
	/* vendor_id: foreign key for table ap_suppliers. */
	,expected_receipt_date
	/* expected_receipt_date: Date when the PO was received or should be received. This data is the date that the
	   frontend user can see and is user provided (not system) but you can use current date and time (SYSDATE) for this too.
	*/
	,validation_flag
	/* validation_flag: Column that indicates whether the import program should do a check on the data in the rows first
	   before trying to import. It is best to use Y (uppercase) to always have it check first.
	*/
	,org_id
	/* org_id: This is the operating unit identifier (foreign key hr_all_operating_units) and can also be found on
	   table po_headers_all and po_lines_all with the same column name "org_id". Note that this is different from the
	   "organization_id" column on mtl_system_items_b table.
			- org_id			= operating unit id
			- organization_id	= inventory organization id
	*/
	)
VALUES
	(rcv_headers_interface_s.nextval
	,rcv_interface_groups_s.nextval
	,'PENDING'
	,'VENDOR'
	,'NEW'
	,SYSDATE
	,0
	,0
	,ap_suppliers.vendor_id
	,SYSDATE
	,'Y'
	,po_headers_all.org_id / po_lines_all.org_id
	);
	
-- The second one is:
INSERT INTO rcv_transactions_interface
	(interface_transaction_id
	/* interface_transaction_id: this is a unique identifier for rcv_transactions_interface table. Although
	   the value entered here will not be carried or pass to other table when importing, it is strongly recommended
	   to use the existing database sequence rcv_transactions_interface_s so the entered row will be unique and will
	   also not interrupt other future insert on this table.
	*/
	,group_id
	/* group_id: this should be the same with related group_id on rcv_headers_interface. This is to identify the
	   rows as a batch for the import program.
	*/
	,last_update_date
	/* last_update_date: standard column of Oracle tables. Same with rcv_headers_interface table. Just use
	   current date and time (or SYSDATE).
	*/
	,last_updated_by
	/* last_updated_by: another standard column of Oracle tables. Just use 0 (zero) for now. */
	,creation_date
	/* creation_date: another standard column of Oracle tables. Just also use current date and time (SYSDATE) */
	,created_by
	/* created_by: another standard column of Oracle tables. Just use 0 (zero) for now. */
	,last_update_login
	/* last_update_login: same description as above. Just use 0 (zero) for now. */
	,transaction_type
	/* transaction_type: I am not sure about this but just use "PENDING" for now. */
	,transaction_date
	/* transaction_date: This column will be seen by the frontend user and usually denotes when did the receiving
	   transaction happen. This is also user provided and can be current date and time (SYSDATE).
	*/
	,processing_status_code
	/* processing_status_code: same with rcv_headers_interface. Just use "PENDING" so it can be picked up by import
	   program.
	*/
	,processing_mode_code
	/* processing_status_code: I am not sure about this column but just use "BATCH" for now. */
	,transaction_status_code
	/* transaction_status_code: I am not sure about this column but just use "PENDING" for now. */
	,po_header_id
	/* po_header_id: foreign key for po_headers_all. This is to identify what purchase order is referenced. */
	,po_line_id
	/* po_line_id: foreign key for po_lines_all. This is to identify what purchase order line is referenced. */
	,item_id
	/* item_id: foreign key for mtl_system_items_b and can also be found on po_lines_all with same name column.
	   Used to identify what inventory item is referenced.
    */
	,quantity
	/* quantity: amount that should be received. This should not be more than what is in quantity of the purchase order
	   lines referenced. This is user provided.
	*/
	,unit_of_measure
	/* unit_of_measure: unit of measure of the entered quantity. If this is different with what is on the unit_meas_lookup_code
	   (and the value is correct and existing on Oracle) there is a process that this is converted. I am also not sure but
	   I think the import program will automatically do this but for now just use the value on column unit_meas_lookup_code of
	   the purchase order lines referenced.
	*/
	,po_line_location_id
	/* po_line_location_id: foreign key for po_line_locations_all. */
	,po_distribution_id
	/* po_distribution_id: foreign key for po_distributions_all. It is not included in the above sample but you can get this by
	   just connecting the table with po_line_locations_all table:
				po_distributions_all.po_line_id			= po_line_locations_all.po_line_id
				po_distributions_all.line_location_id	= po_line_locations_all.line_location_id
	*/
	,auto_transact_code
	/* auto_transact_code: I am not sure about this column but just enter a null (the function null and not characters/string) or blank value. Or you can removed this from
	   the insert. Do what makes your insert script successful.
	*/
	,receipt_source_code
	/* receipt_source_code: Same with the other table. Just use "VENDOR" for now. */
	,to_organization_code
	/* to_organization_code: This is user provided. This pertains to the inventory organization code (organization_id on mtl_system_items_b
	   is related to this but not the exact column)
	*/
	,source_document_code
	/* source_document_code: I am not sure about this column but just use "PO" for now. */
	,header_interface_id
	/* header_interface_id: The value here should be the same with the related entry on the first interface table. */
	,validation_flag
	/* validation_flag: same with the first interface table. Just use "Y" (uppercase) for now. */
	,org_id
	/* org_id: same with the first interface table. */
	)
VALUES
	(rcv_transactions_interface_s.nextval
	,rcv_interface_groups_s.currval
	,SYSDATE
	,0
	,SYSDATE
	,0
	,0
	,'PENDING'
	,SYSDATE
	,'PENDING'
	,'BATCH'
	,'PENDING'
	,--po_headers_all.po_header_id
	,--po_lines_all.po_line_id
	,--po_lines_all.item_id / mtl_system_items_b.inventory_item_id
	,--(This is user provided and should not be greater than the quantity on the row on po_lines_all referenced)
	,--po_lines_all.unit_meas_lookup_code
	,--po_line_locations_all.line_location_id
	,--po_distributions_all.po_distribution_id
	,NULL
	,'VENDOR'
	,--(This is user provided and organization code should exist in the database)
	,'PO'
	,rcv_headers_interface_s.currval
	,'Y'
	,--po_headers_all.org_id / po_lines_all.org_id
	);
