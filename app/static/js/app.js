(function() {
  (function($) {
    var init, initAjaxCSRF, initBreadcrumb, initDeletion, initFileSelection, initNewFolder, initRename, initTooltip, initUpload, insertObject, populateMeta, renameInput, initDownload;
    $.fn.singleDoubleClick = function(singleClickCallback, doubleClickCallback, timeout) {
      return this.each(function() {
        var clicks, self;
        clicks = 0;
        self = this;
        return $(this).click(function(event) {
          clicks++;
          if (clicks === 1) {
            return setTimeout(function() {
              if (clicks === 1) {
                singleClickCallback.call(self, event);
                if ($(".selected").length > 0){
                  $('#download_file').prop('disabled', false);
                  $('#delete_object').prop("disabled", false);
                }else if($(".selected").length === 0){
                  $('#download_file').prop('disabled', true);
                  $('#delete_object').prop("disabled", true);
                }
              } else {
                doubleClickCallback.call(self, event);
              }
              return clicks = 0;
            }, timeout || 250);
          }
        });
      });
    };
    init = function() {
      initAjaxCSRF();
      initBreadcrumb();
      initFileSelection();
      initNewFolder();
      initUpload();
      initRename();
      initDeletion();
      initDownload();
      return initTooltip();
    };
    initAjaxCSRF = function() {
      return $.ajaxSetup({
        headers: {
          'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr("content")
        }
      });
    };
    initTooltip = function() {
      return $('[data-toggle="tooltip"]').tooltip();
    };
    initNewFolder = function() {
      $("#new_folder").on("click", function() {
        var names, newFolder;
        $(this).prop("disabled", true);
        insertObject("directory", true);
        names = [];
        $(".object").each(function() {
          var basename;
          basename = $(this).data("basename");
          if (basename.indexOf("Untitled Folder") > -1) {
            basename = basename.replace("Untitled Folder", "").trim();
            if (!basename) {
              basename = 1;
            }
            return names.push(parseInt(basename, 10));
          }
        });
        if (names.length > 0) {
          newFolder = "Untitled Folder " + (Math.max.apply(Math, names) + 1);
        } else {
          newFolder = "Untitled Folder";
        }
        return $("#input-folder").val("" + newFolder).focus().select();
      });
      $("#file_system").on(
          {"focusout": function(e) {
            $(this).parent().trigger("submit");
            return false;
          },
          "keydown": function(e){
            if(e.keyCode==13){
              return false;
            }}}, ".object .name #input-folder");
      return $("#file_system").on("submit", "#create-form", function(e) {
        var currentObject;
        e.preventDefault();
        if (!$("#input-folder").val()) {
          $(this).parents("object-container").remove();
          $("#new_folder").prop("disabled", false);
          return false;
        }
        currentObject = $(this).parents(".object");
        currentObject.first().addClass("uploading");
        return $.ajax({
          url: "/manager/put/directory",
          data: {
            path: $("#file_system").data("dirpath"),
            dirName: $("#input-folder").val()
          },
          type: "PUT",
          dataType: "json",
          success: function(response){
            populateMeta(currentObject, "directory", response);
         },
          error: function(response){
            alert("Failed to create the folder");
            return $(this).parents(".object").removeClass("uploading").find("input-folder").focus().select();
          },
          complete: function(response){
             return $("#new_folder").prop("disabled", false);
          }
        });
      });
    };
    initBreadcrumb = function() {
      var currentLink, fullPath;
      fullPath = '' + $("#file_system").data("dirpath");
      if (fullPath === '/') {
        return false;
      }
      currentLink = "/home";
      return $.each(fullPath.split('/'), function(index, node) {
        currentLink += "/" + node;
        return $(".breadcrumb").append("<li class=\"breadcrumb-item\"><a href=\"" + currentLink + "\">" + node + "</a></li>");
      });
    };
    initUpload = function() {
      $("#fileupload").on("change", function() {
        var files, formData, maxFileSize, upload;
        files = this.files;
        upload = true;
        maxFileSize = $("#file_system").data("maxfilesize") - 512;
        $.each(files, function(index, file) {
          if (file.name.indexOf('/') !== -1) {
            alert("File " + file.name + " is illegal");
            upload = false;
            return false;
          }
          else if (file.size > maxFileSize) {
            alert("File " + file.name + " is too large");
            upload = false;
            return false;
          }
        });
        function onprogress(evt){
            var loaded = evt.loaded;                  //已经上传大小情况
            var tot = evt.total;                      //附件总大小
            var per = Math.floor(100*loaded/tot);      //已经上传的百分比
            $(".progress-bar").html( per +"%" );
            $(".progress-bar").css("width" , per +"%");
        }
        if (upload){
          $('.modal-body').append('\n   <div class="progress progress-striped active" id="upload-progress">\n    <div class="progress-bar progress-bar-success" role="progressbar" style="width: 0%;">0%</div>\n   </div>');
          $('#myModal').modal('show');
          $('#myModal').on('hidden.bs.modal', function () {
            $('.modal-body').children().remove();
          });
        }
        formData = new FormData($("#upload")[0]);
        return $.ajax({
          url: "/manager/put/file",
          type: "POST",
          dataType: "json",
          data: formData,
          cache: false,
          contentType: false,
          processData: false,
          xhr: function(){
　　　　　　var xhr = $.ajaxSettings.xhr();
　　　　　　if(onprogress && xhr.upload && upload) {
　　　　　　　　xhr.upload.addEventListener("progress" , onprogress, false);
　　　　　　　　return xhr;
　　　　　　}
　　　　}
        }).success(function(responses) {
          $(responses.errors).each(function(index, error) {
            return console.log(error);
          });
          return $(responses.success).each(function(index, file) {
            var newObject;
            newObject = $(insertObject("file", false)).children();
            populateMeta(newObject, "file", file);
            return initFileSelection(newObject);
          });
        }).fail(function() {
          return alert("Upload failed");
        });
      });
    };
    insertObject = function(objectType, newObject) {
      var name, nameInput, objectModel;
      nameInput = "<form id=\"create-form\">\n    <label for=\"input-folder\" class=\"sr-only\">New folder</label>\n    <input type=\"text\" placeholder=\"Folder Name\" id=\"input-folder\" class=\"text-center\">\n    <input type=\"hidden\" name=\"_method\" value=\"PUT\">\n</form>";
      if (newObject) {
        name = nameInput;
      } else {
        name = null;
      }
      objectModel = "<div class=\"col-xs-4 col-sm-3 col-md-2 object-container\">\n    <div data-basename=\"\" data-mime=\"\" data-filetype=\"\" class=\"object object-new\">\n        <div class=\"icon-container\">\n            <div class=\"icon-base " + objectType + "\"></div>\n            <div class=\"icon-main\"></div>\n        </div>\n        <div class=\"name-container\">\n            <div title=\"\" class=\"name text-primary\" role=\"button\">\n               " + name + "\n            </div>\n            <div class=\"meta-info text-muted\"></div>\n        </div>\n    </div>\n</div>";
      if (objectType === "directory") {
        return $(objectModel).prependTo("#file_system");
      } else if (objectType === "file") {
        return $(objectModel).hide().appendTo("#file_system").fadeIn(500);
      }
    };
    populateMeta = function(object, objectType, objectMeta) {
      var link, pathList, sPath, filename;
      pathList = objectMeta.path.split('/');
      filename = pathList.pop();
      sPath = pathList.join('/');
      if (objectType === 'file') {
        link = "/preview/" + sPath + "?filename=" + filename;
      }else{
        if (!objectMeta.pathinfo.dirname) {
          link = "/home" + objectMeta.path;
        } else {
          link = "/home/" + objectMeta.path;
        }
      }
      return object.removeClass("uploading").removeClass("renaming").removeClass("object-new").data("filetype", objectMeta.mime).data("basename", objectMeta.pathinfo.basename).data("fullpath", objectMeta.path).find(".name").empty().append("<a class=\"link\" href=\"" + link + "\">" + objectMeta.pathinfo.basename + "</a> <a href=\"#\" class=\"hide rename\"><span class=\"glyphicon glyphicon-pencil\" aria-hidden=\"true\"></a>").parent().children(".meta-info").empty().append("<div class=\"meta-info text-muted\">Just now</div>");
    };
    initRename = function() {
      $("#file_system").on("click", ".object .rename", function(e) {
        e.preventDefault();
        renameInput($(this).parents(".object"));
        return false;
      });
      $("#file_system").on("focusout", ".object .name #input-file", function() {
        $(this).parent().trigger("submit");
        return false;
      });
      return $("#file_system").on("submit", "#rename-form", function(e) {
        var currentObject, fileType, newName, oldName;
        e.preventDefault();
        currentObject = $(this).parents(".object");
        oldName = currentObject.data("basename");
        newName = $(this).children("#input-file").val();
        fileType = currentObject.data("filetype");
        if (!newName || (oldName === newName)) {
          $(this).parent().find("a").show();
          $(this).remove();
          return false;
        }
        currentObject.addClass("renaming");
        $.ajax({
          url: "/manager/move",
          data: {
            path: $("#file_system").data("dirpath"),
            oldName: oldName,
            newName: newName,
            fileType: fileType
          },
          type: "POST",
          dataType: "json"
        }).success(function(response) {
          currentObject.find(".name").empty();
          return populateMeta(currentObject, fileType, response);
        }).fail(function() {
          alert("Failed to rename the object");
          currentObject.removeClass("renaming").find(".name a").show();
          return currentObject.find("#rename-form").remove();
        });
        return false;
      });
    };
    renameInput = function(object) {
      var nameInput, oldName;
      oldName = object.data("basename");
      nameInput = "<form id=\"rename-form\">\n    <label for=\"input-file\" class=\"sr-only\">File Name</label>\n    <input type=\"text\" placeholder=\"Folder Name\" id=\"input-file\" class=\"text-center\" value=\"" + oldName + "\"  onkeydown=\"if(event.keyCode==13){return false;}\">\n</form>";
      object.find(".name a").hide();
      return $(nameInput).prependTo(object.find(".name")).find("#input-file").focus().select();
    };
    initFileSelection = function(object) {
      if (!object) {
        object = $("#file_system .object");
      }
      return object.singleDoubleClick((function() {
        return $(this).toggleClass("selected");
      }), (function() {
        if ($(this).data("filetype") === "directory") {
          $("#file_system").addClass("loading");
        }
        return window.location = $(this).find(".link").attr("href");
      }));
    };
    initDeletion = function() {
      return $("#delete_object").on("click", function() {
        var selectedFiles;
        selectedFiles = $(".selected");
        if (selectedFiles.length === 0) {
          alert("Please select object(s) first");
          return false;
        }
        return selectedFiles.each(function(index, file) {
          var fileType;
          fileType = $(file).data("filetype");
          return $.ajax({
            url: "/manager/delete",
            data: {
              path: $(file).data("fullpath"),
              fileType: fileType
            },
            type: "DELETE",
            dataType: "json"
          }).success(function() {
            return $(file).fadeOut(500, function() {
              $('#download_file').prop('disabled', true);
              $('#delete_object').prop("disabled", true);
              return $(this).parent().remove();
            });
          }).fail(function() {
            return alert("Failed to delete " + fileType + " " + ($(file).data("basename")));
          }).done(function() {
            return $("#delete_object").prop("disabled", false);
          });
        });
      });
    };
    initDownload = function() {
      return $("#download_file").on("click", function() {
        var selectedFiles, filePath, DownLoadFile;
        selectedFiles = $(".selected");
        if (selectedFiles.length === 0) {
        $(this).prop("disabled", true);
          alert("Please select File");
          return false;
        }
        filePath = [];
        selectedFiles.each(function(index, file) {
          filePath.push($(file).data("fullpath"));
        });
        DownLoadFile = function (options) {
          var config, $iframe, $form;
          config = $.extend(true, { method: 'post' }, options);
          $iframe = $('<iframe id="down-file-iframe" />');
          $form = $('<form target="down-file-iframe" method="' + config.method + '" />');
          $form.append('<input type="hidden" name="csrf_token" value="' + $('meta[name="csrf-token"]').attr("content") + '" />');
          $form.attr('action', config.url);
          for (var key in config.data) {
            $form.append('<input type="hidden" name="' + key + '" value="' + config.data[key].join('///') + '" />');
          }
          $iframe.append($form);
          $(document.body).append($iframe);
          $form[0].submit();
          $iframe.remove();
        };
        return DownLoadFile({url: '/manager/download', data:{path:filePath}});
      });
    };
    initMove = function () {

    };
    return init();
  })(jQuery);

}).call(this);

//# sourceMappingURL=app.js.map
