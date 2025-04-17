# Setting up the program
1. Load the sheetid.txt and credentials.json
2. Run the following commands to create local variables:
`FILE_SHEET=$(cat sheetid.txt)`
`export TEST_SHEETID="$FILE_SHEET"`
`FILE_CONTENT=$(cat credentials.json)`
`export API_KEY="$FILE_CONTENT"`
