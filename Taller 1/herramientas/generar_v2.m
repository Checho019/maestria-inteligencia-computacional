function generar_v2
% Corre el live script de la version 2, guarda sus figuras en v2/informe/figuras
% y deja el .mlx ejecutado en v2/. Se llama desde la carpeta Taller 1.
cd v2
copyfile('../data_banknote_authentication.txt', '.');
copyfile('../iris.dat', '.');
if exist('Taller1_Perceptron_Adaline_LiveScript.mlx', 'file')
    delete('Taller1_Perceptron_Adaline_LiveScript.mlx')   % el mlx ensombrece al .m
end
correr('Taller1_Perceptron_Adaline_LiveScript.m')
figs = findobj('Type', 'figure');
[~, orden] = sort([figs.Number]);
figs = figs(orden);
if ~exist('informe/figuras', 'dir'), mkdir('informe/figuras'); end
% Cada figura se exporta al mismo ancho con que entra al informe, asi la letra
% de 9 puntos se ve a 9 puntos en el PDF, cerca de los 11 del cuerpo del texto
tam = [13 6.5; 15 6; 12 6.5; 12 8.5; 11 6];
for k = 1:numel(figs)
    figs(k).Theme = 'light';
    set(findall(figs(k), '-property', 'FontSize'), 'FontSize', 9)
    % en modo batch la Position de la figura solo se respeta en la primera,
    % por eso el tamano se fija en la exportacion
    exportgraphics(figs(k), fullfile('informe', 'figuras', sprintf('fig%02d.png', k)), ...
        'Resolution', 300, 'Width', tam(k, 1), 'Height', tam(k, 2), 'Units', 'centimeters')
end
close all
mlx = fullfile(pwd, 'Taller1_Perceptron_Adaline_LiveScript.mlx');
matlab.internal.liveeditor.openAndSave(fullfile(pwd, 'Taller1_Perceptron_Adaline_LiveScript.m'), mlx);
matlab.internal.liveeditor.executeAndSave(mlx);
close all
cd ..
end

function correr(nombre)
% El script empieza con clear, por eso corre en su propio espacio de trabajo
run(nombre);
end
