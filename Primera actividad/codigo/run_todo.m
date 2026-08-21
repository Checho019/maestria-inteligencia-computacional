%% =======================================================================
%  Corre toda la actividad de principio a fin.
%
%  Antes de correr: descomprimir bank+marketing.zip y ecoli.zip dentro de
%  "Primera actividad/data" de modo que queden
%       data/ecoli/ecoli.data
%       data/bank/bank-full.csv
%
%  Todo usa semilla fija, asi que los resultados se repiten exactamente.
%  Tarda unos 20 minutos: la mitad es la simulacion del paso 0 y el resto
%  el SVM y el KNN del dataset Bank.
% =======================================================================
clear; clc; close all;

base = fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(base, 'codigo'));
addpath(fullfile(base, 'codigo', 'funciones'));

% carpetas de salida
carpetas = {fullfile(base,'resultados','ecoli','figuras'), ...
            fullfile(base,'resultados','ecoli','etapas'), ...
            fullfile(base,'resultados','bank','figuras'), ...
            fullfile(base,'resultados','bank','etapas'), ...
            fullfile(base,'resultados','validacion')};
for i = 1:numel(carpetas)
    if ~exist(carpetas{i}, 'dir'), mkdir(carpetas{i}); end
end

% los dos libros se borran para que no queden hojas viejas de corridas previas
xls = {fullfile(base, 'Resultados_Ecoli.xlsx'), fullfile(base, 'Resultados_Bank.xlsx')};
for i = 1:numel(xls)
    if exist(xls{i}, 'file'), delete(xls{i}); end
end

scripts = {'paso0_validar_pruebas', ...
           'paso1_exploracion_ecoli', 'paso2_pruebas_ecoli', ...
           'paso3_etapas_ecoli',      'paso4_modelos_ecoli', ...
           'paso1_exploracion_bank',  'paso2_pruebas_bank', ...
           'paso3_etapas_bank',       'paso4_modelos_bank', ...
           'paso5_resumen'};

t_total = tic;
for i = 1:numel(scripts)
    fprintf('\n\n=================================================\n');
    fprintf(' [%d/%d] %s\n', i, numel(scripts), scripts{i});
    fprintf('=================================================\n');
    t = tic;
    correr(scripts{i});                 % ver la funcion de abajo
    fprintf('>>> %s listo en %.1f s\n', scripts{i}, toc(t));
end
fprintf('\n\nTODO LISTO en %.1f minutos.\n', toc(t_total)/60);
fprintf('Excel:   %s\n', xls{1});
fprintf('         %s\n', xls{2});
fprintf('Figuras: %s\n', fullfile(base,'resultados'));


function correr(nombre)
% Cada paso se lanza desde dentro de una funcion para que tenga su propio
% espacio de variables. Si se llamaran con run() directamente, el "clear" con
% el que empieza cada script borraria tambien las variables de este archivo.
run(nombre);
end
