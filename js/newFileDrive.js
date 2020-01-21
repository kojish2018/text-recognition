
var ss = SpreadsheetApp.openById('spreadsheetID')
var sh = ss.getSheetByName('sheetName')
var sh_data = sh.getDataRange().getValues()[0];
var sh_lastColumn = sh.getLastColumn();

  var Drive = function(cus, folderId, fileId){
    this.cus = cus;
    this.folderId = folderId;
    this.fileId = fileId;
  }
  
  var cusList = ['names']
  var folderIdList = ['folderIDs']
  
  var folderList = [];
  for(i=0; i<cusList.length; i++){
    var folder = new Drive(cusList[i],folderIdList[i]);
    folderList.push(folder);
  }

function newFile(){
  var filesDrive = updateCheck();
  
  for(i=0;i<filesDrive.length;i++){
    if(sh_data.indexOf(filesDrive[i][0].fileId) == -1){
      sh.getRange(1,sh_lastColumn+1+i).setValue(filesDrive[i][0].fileId);
    }
  }
  
    //バケット名の設定
  var bucket = "bucketName";
  
  //アップロード先フォルダを指定
  var folders = "public/" + filesDrive[0][0].cus;
  
  var token = ScriptApp.getOAuthToken()
  
  if(filesDrive.length != 0){
  for(i=0; i<filesDrive.length;i++){
  //指定ファイルを取得
  var blob = DriveApp.getFileById(filesDrive[i][0].fileId).getBlob();
  var bytes = blob.getBytes();
  Logger.log(bytes)
  
  var pngBlob = Utilities.newBlob(bytes, 'application/png', 'new.png')

  var url = "https://www.googleapis.com/upload/storage/v1/b/" + bucket + "/o?uploadType=media&name=" + filesDrive[i][0].cus;

   

  var options = {
    'method' : "POST",
    'payload': bytes,
    'headers' : {'Authorization': 'Bearer '+ token,
                 'Content-Type': pngBlob.getContentType(),
                 "muteHttpExceptions": true
              },
  };

  var response = UrlFetchApp.fetch(url, options);
  
    
  }
    for(i=0; i<filesDrive.length;i++){
    var url = "cloudfunctions url"
    var options = {
    'method' : "POST",
    'payload': JSON.stringify(filesDrive[i][0].cus),
    'headers' : {'Authorization': 'Bearer '+ token,
                 'Content-Type': "application/json",
                 "muteHttpExceptions": true
              },
      
    };
      
      var response = UrlFetchApp.fetch(url, options);
      Logger.log(response)
  }
  
}
}

function updateCheck() {
  var allFilesDrive = [];
  
  for(i=0; i<cusList.length; i++){
    var targetFolder = DriveApp.getFolderById(folderList[i].folderId);
    var folders = targetFolder.getFolders();
    var files = targetFolder.getFiles();
  
  var allFilesId = getAllFilesId(targetFolder, cusList[i])
  
  if(allFilesId.length !== 0)allFilesDrive.push(allFilesId);
  }
  return allFilesDrive
}

      
function getAllFilesId(targetFolder, cus){
    var filesIdList = [];
    
    var files = targetFolder.getFiles();
    while(files.hasNext()){
      var fileId = new Drive(cus, '', files.next().getId())
      filesIdList.push(fileId);
    }
    
    var child_folders = targetFolder.getFolders();
    while(child_folders.hasNext()){
      var child_folder = child_folders.next();
      filesIdList = filesIdList.concat( getAllFilesId(child_folder,cus) );
    }
    return filesIdList;
  }



