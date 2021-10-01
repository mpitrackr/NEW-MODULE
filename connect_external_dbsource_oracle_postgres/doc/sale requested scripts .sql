select
  ooha.order_number "Sales Order Number",
  ooha.header_id "SO Header ID",
  ooha.flow_status_code "Order Status",
  ooha.ordered_date "Sales Order Date",
  oola.line_number "Sales Order Line",
  oola.shipment_number "Shipment Line Number",
  oola.flow_status_code "Sales Order Status",
  hp.party_name "Customer",
  hp.party_id "Customer ID",
  oola.ordered_item "Item",
  uom.unit_of_measure "UOM",
  msib.description "Description",
  oola.pricing_quantity "Quantity"
from
  oe_order_headers_all ooha,
  oe_order_lines_all oola,
  mtl_system_items_b msib,
  hz_parties hp,
  hz_cust_accounts hca,
  mtl_units_of_measure_vl uom
where
  ooha.header_id = oola.header_id
  and ooha.org_id = oola.org_id
  and oola.open_flag = 'Y'
  and oola.ordered_item = msib.segment1
  and uom.uom_code = oola.pricing_quantity_uom
  and hca.cust_account_id = ooha.sold_to_org_id
  and hp.party_id = hca.party_id
  and ooha.ship_from_org_id = msib.organization_id
  and oola.flow_status_code = 'AWAITING_SHIPPING'
  and ooha.flow_status_code = 'BOOKED' 
order by
  ooha.order_number,
  oola.line_number,
  ooha.header_id

-- Response:
{'Sales Order Number': 300000009, 'SO Header ID': 5061, 'Order Status': 'BOOKED', 'Sales Order Date': datetime.datetime(2016, 1, 12, 20, 26, 45), \
'Sales Order Line': 1, 'Shipment Line Number': 1, 'Sales Order Status': 'AWAITING_SHIPPING', 'Customer': 'International Family Food Services Inc.',\
 'Customer ID': 8465, 'Item': 'BRC-0445C', 'UOM': 'BAG', 'Description': 'Regular Breadcrumbs; 1 kg x 10 pks/bag', 'Quantity': 15}
