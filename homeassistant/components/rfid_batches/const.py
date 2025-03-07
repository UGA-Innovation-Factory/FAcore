"""Constants for the RFID Batches integration."""

DOMAIN = "rfid_batches"

CONF_NAME = "Equipment Name"
CONF_TAG_ID = "tag_id"

CONF_CARD_TYPE = "Tag Type"
CONF_CARD_TYPE_TAG = "HASS Tag"
CONF_CARD_TYPE_BATCH = "Pecan Batch"
CONF_CARD_TYPE_EQUIPMENT = "Equipment"
CONF_CARD_TYPE_NONE = "Unassigned"

CONF_SENSORS = "Sensors"
CONF_ACTUATORS = "Machine Parameters"

CONF_STEP = "Active Batch Step"
CONF_STEP_RECEIVE = "Receiveing"
CONF_STEP_CHILL = "Chilling"
CONF_STEP_CONDITION = "Conditioning"
CONF_STEP_DRY = "Drying"
CONF_STEP_CRACK_JC = "JC Cracking"
CONF_STEP_CRACK_MEYER = "Meyer Cracking"
CONF_STEP_SHELL = "Shelling"
CONF_STEP_SORT = "Sorting"
CONF_STEP_INSPECT_MOISTURE = "Inspecting Moisture"
CONF_STEP_INSPECT_CRACK = "Inspecting Cracks"
CONF_STEP_INSPECT_DISTRIBUTION = "Inspecting Distribution"
CONF_STEP_INSPECT_YIELD = "Inspecting Yield"
CONF_STEPS = [
    CONF_STEP_RECEIVE,
    CONF_STEP_CHILL,
    CONF_STEP_CONDITION,
    CONF_STEP_DRY,
    CONF_STEP_CRACK_JC,
    CONF_STEP_CRACK_MEYER,
    CONF_STEP_SHELL,
    CONF_STEP_SORT
]
CONF_PENDING = "Pending"
CONF_ACTIVE = "Active"
CONF_COMPLETE = "Complete"

CONF_BATCH_ID = "Batch ID"
CONF_BATCH_CREATION_DATE = "Creation Date"
CONF_PARENT_BATCH_ID = "Parent Batch ID"

CONF_CONDITIONING_PARAM_TEMP = "Conditioning Temperature"

CONF_MEYER_PARAM_SETSCREW = "Meyer Cracker Set Screw"
CONF_MEYER_PARAM_SPEED = "Meyer Cracker Speed"

CONF_JC_PARAM_HEIGHT = "JC Cracker Height"
CONF_JC_PARAM_SPEED = "JC Cracker Speed"
CONF_JC_PARAM_THROUGHPUT = "JC Cracker Throughput"
CONF_JC_PARAM_ANGLE = "JC Cracker Angle"

CONF_SHELLER_PARAM_ANGLE = "Sheller Angle"
CONF_SHELLER_PARAM_DRUM = "Sheller Drum Speed"
CONF_SHELLER_PARAM_PADDLE = "Sheller Paddle Speed"
