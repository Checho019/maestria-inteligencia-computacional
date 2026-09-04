function generar
% Corre procesar_bank.m, guarda cada figura en figuras/ y deja el .mlx ejecutado.
% Se llama desde la carpeta Exposicion Bank.
correr('procesar_bank')
figs = findobj('Type', 'figure');
[~, orden] = sort([figs.Number]);
figs = figs(orden);
for k = 1:numel(figs)
    figs(k).Theme = 'light';
    figs(k).Position = [50 50 1300 650];
    exportgraphics(figs(k), fullfile('figuras', sprintf('fig%02d.png', k)), 'Resolution', 130)
end
close all
mlx = fullfile(pwd, 'procesar_bank.mlx');
matlab.internal.liveeditor.openAndSave(fullfile(pwd, 'procesar_bank.m'), mlx);
matlab.internal.liveeditor.executeAndSave(mlx);
close all
disp('>>> listo')
end

function correr(nombre)
run(nombre);
end
