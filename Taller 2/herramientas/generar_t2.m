function generar_t2
% Corre el live script del Taller 2, exporta las figuras a informe/figuras al
% ancho con que entran al informe y deja el .mlx ejecutado. Se llama desde Taller 2.
copyfile('datos/*', '.');
if exist('Taller2_MLP_Backpropagation_LiveScript.mlx', 'file')
    delete('Taller2_MLP_Backpropagation_LiveScript.mlx')
end
correr('Taller2_MLP_Backpropagation_LiveScript.m')
figs = findobj('Type', 'figure');
[~, orden] = sort([figs.Number]);
figs = figs(orden);
tam = [12 6.5; 12 6.5; 15 15; 15 7.5; 15 11];
for k = 1:numel(figs)
    figs(k).Theme = 'light';
    set(findall(figs(k), '-property', 'FontSize'), 'FontSize', 9)
    exportgraphics(figs(k), fullfile('informe', 'figuras', sprintf('fig%02d.png', k)), ...
        'Resolution', 300, 'Width', tam(min(k, end), 1), 'Height', tam(min(k, end), 2), 'Units', 'centimeters')
end
close all
mlx = fullfile(pwd, 'Taller2_MLP_Backpropagation_LiveScript.mlx');
matlab.internal.liveeditor.openAndSave(fullfile(pwd, 'Taller2_MLP_Backpropagation_LiveScript.m'), mlx);
matlab.internal.liveeditor.executeAndSave(mlx);
close all
mlx2 = fullfile(pwd, 'Dataset_train_test_T2.mlx');
if exist(mlx2, 'file'), delete(mlx2), end
matlab.internal.liveeditor.openAndSave(fullfile(pwd, 'Dataset_train_test_T2.m'), mlx2);
matlab.internal.liveeditor.executeAndSave(mlx2);
close all
end

function correr(nombre)
run(nombre);
end
