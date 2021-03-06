// Copyright 2014 The Oppia Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * @fileoverview Directives that are not associated with reusable components.
 * NB: Reusable component directives should go in the components/ folder.
 *
 * @author sll@google.com (Sean Lip)
 */

// HTML bind directive that trusts the value it is given and also evaluates
// custom directive tags in the provided value.
oppia.directive('angularHtmlBind', ['$compile', function($compile) {
  return {
    restrict: 'A',
    scope: {
      varToBind: '=angularHtmlBind'
    },
    link: function(scope, elm, attrs) {
      scope.$watch('varToBind', function(newValue, oldValue) {
        elm.html(newValue);
        $compile(elm.contents())(scope);
      });
    }
  };
}]);


oppia.directive('mathjaxBind', [function() {
  return {
    restrict: 'A',
    controller: ['$scope', '$element', '$attrs', function($scope, $element, $attrs) {
      $scope.$watch($attrs.mathjaxBind, function(value) {
        var $script = angular.element('<script type="math/tex">')
          .html(value == undefined ? '' : value);
        $element.html('');
        $element.append($script);
        MathJax.Hub.Queue(['Reprocess', MathJax.Hub, $element[0]]);
      });
    }]
  };
}]);


// Highlights the text of an input field when it is clicked.
oppia.directive('selectOnClick', [function() {
  return {
    restrict: 'A',
    link: function(scope, elm, attrs) {
      elm.bind('click', function() {
        this.select();
      });
    }
  };
}]);


oppia.directive('whenScrolledToBottom', [function() {
  return function(scope, elm, attr) {
    var raw = elm[0];

    elm.bind('scroll', function() {
      if (raw.scrollTop + raw.offsetHeight >= raw.scrollHeight) {
        scope.$apply(attr.whenScrolled);
      }
    });
  };
}]);


// A popover that is shown when its label is hovered or clicked upon, and
// disappears when focus moves away from its label.
oppia.directive('customPopover', ['$sce', function($sce) {
  return {
    restrict: 'A',
    template: '<div style="cursor: pointer;" ng-click="showPopover()"><[label]></div>',
    link: function(scope, elt, attrs) {
      scope.label = attrs.popoverLabel;
      $(elt).popover({
        trigger: 'hover',
        html: true,
        content: $sce.getTrustedHtml('<pre class="oppia-pre-wrapped-text">'
	  + attrs.popoverText + '</pre>'),
        placement: attrs.popoverPlacement
      });
    },
    controller: ['$scope', '$element', function($scope, $element) {
      $scope.isShown = false;

      $element.on('shown.bs.popover', function() {
        $scope.isShown = true;
      });
      $element.on('hidden.bs.popover', function() {
        $scope.isShown = false;
      });

      $scope.showPopover = function() {
        if (!$scope.isShown) {
          $element.popover('show');
        }
      };
    }]
  };
}]);

// When set as an attr of an <input> element, moves focus to that element
// when a 'focusOn' event is broadcast.
oppia.directive('focusOn', [function() {
  return function(scope, elt, attrs) {
    scope.$on('focusOn', function(e, name) {
      if (name === attrs.focusOn) {
        elt[0].focus();
      }
    });
  };
}]);

oppia.directive('imageUploader', [function() {
  return {
    restrict: 'E',
    scope: {
      height: '@',
      onFileChanged: '=',
      width: '@'
    },
    templateUrl: 'components/imageUploader',
    link: function(scope, elt, attrs) {
      var onDragEnd = function(e) {
        e.preventDefault();
        $(elt).removeClass('image-uploader-is-active');
      };

      $(elt).bind('drop', function(e) {
        onDragEnd(e);
        scope.onFileChanged(
          e.originalEvent.dataTransfer.files[0],
          e.originalEvent.dataTransfer.files[0].name);
      });

      $(elt).bind('dragover', function(e) {
        e.preventDefault();
        $(elt).addClass('image-uploader-is-active');
      });

      $(elt).bind('dragleave', onDragEnd);

      // We generate a random class name to distinguish this input from
      // others in the DOM.
      scope.fileInputClassName = (
        'image-uploader-file-input' + Math.random().toString(36).substring(5));
      angular.element(document).on(
          'change', '.' + scope.fileInputClassName, function(evt) {
        scope.onFileChanged(
          evt.currentTarget.files[0],
          evt.target.value.split(/(\\|\/)/g).pop());
      });
    }
  };
}]);
