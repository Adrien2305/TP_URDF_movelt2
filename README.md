# 🦾 Robot Arm — URDF / Xacro & MoveIt 2

> **Master 1 — Robotique & Systèmes embarqués**  
> TP Robotique Industrielle — K. Ramoth — 2026  
> Technologies : ROS 2 Humble/Jazzy · URDF/Xacro · MoveIt 2 · RViz 2

---

## 1. Présentation du robot

Le robot modélisé est un **bras manipulateur à 4 degrés de liberté** avec une pince à deux doigts.  
Sa chaîne cinématique est la suivante :

```
world (fixe)
  └─ base_link          ← socle fixe (basement + plate meshes)
       └─ base_plate     ← joint1 : révolution Z  (lacet ±180°)
            └─ forward_drive_arm  ← joint2 : révolution X (tangage ±90°)
                 └─ horizontal_arm    ← joint3 : révolution X (tangage ±90°)
                      └─ claw_support      ← joint_claw : révolution Z (±90°)
                           ├─ gripper_right  ← joint4 : prismatique X (0–22 mm)
                           └─ gripper_left   ← joint5 : prismatique X (mimic joint4 ×−1)
```

**Dimensions clés** (issues des images du sujet) :

| Transition         | Hauteur / Distance  |
|--------------------|---------------------|
| base_link → base_plate | 3.07 cm |
| base_plate → forward_drive_arm | 3.5 cm |
| forward_drive_arm → horizontal_arm | 8 cm |
| horizontal_arm → claw_support | 8.2 cm |
| Écart des doigts (max) | 2 × 2.2 cm |

---

## 2. Justification du choix Xacro vs URDF pur

### Choix retenu : **Xacro modulaire**

| Critère | Détail |
|---------|--------|
| **Complexité** | 7 liens + 6 joints + 2 macros d'inertie → le fichier dépasse 300 lignes si tout est en URDF brut |
| **Répétition** | Les deux doigts de la pince ont la même géométrie d'inertie ; les macros `cylinder_inertia` et `box_inertia` évitent la duplication |
| **Lisibilité** | `${PI/2}` est bien plus lisible que `1.5707963` répété 12 fois |
| **Maintenance** | Modifier une propriété globale (masse, échelle) se fait en un seul endroit |

**Avantages** : expressions mathématiques, macros réutilisables, constantes nommées, inclusion de fichiers possible.  
**Inconvénients** : nécessite `xacro` comme dépendance supplémentaire ; le URDF final généré est moins lisible directement.

**Quand aurait-on choisi URDF pur ?** Pour un robot très simple (2–3 liens), ou pour partager le modèle avec des outils ne supportant pas Xacro.

---

## 3. Hypothèses sur les masses, inerties et limites articulaires

### Masses estimées

| Lien                | Masse (kg) | Forme approx. |
|---------------------|------------|---------------|
| base_link           | 0.50       | Cylindre ø14cm, h=3cm |
| base_plate          | 0.20       | Cylindre ø10cm, h=2cm |
| forward_drive_arm   | 0.15       | Boîte 3×8×3 cm |
| horizontal_arm      | 0.15       | Boîte 8×3×3 cm |
| claw_support        | 0.10       | Boîte 4×4×5 cm |
| gripper_right/left  | 0.03       | Boîte 1×4×2 cm |

Les inerties sont calculées analytiquement à partir des formules de solides homogènes (cylindre, pavé).  
*Ces valeurs sont des estimations raisonnables pour un bras de petite taille (type Arduino/servo hobby).*

### Limites articulaires

| Joint       | Type       | Plage          | Effort (N·m) | Vitesse (rad/s) |
|-------------|------------|----------------|--------------|-----------------|
| joint1      | revolute   | [−π, +π]       | 50           | 1.0             |
| joint2      | revolute   | [−π/2, +π/2]   | 30           | 1.0             |
| joint3      | revolute   | [−π/2, +π/2]   | 30           | 1.0             |
| joint_claw  | revolute   | [−π/2, +π/2]   | 20           | 1.0             |
| joint4      | prismatic  | [0, 0.022 m]   | 10           | 0.2 m/s         |
| joint5      | prismatic  | mimic joint4×−1| —            | —               |

---

## 4. Instructions d'installation

### Prérequis

- **Ubuntu 22.04** (Humble) ou **Ubuntu 24.04** (Jazzy)
- ROS 2 installé et sourcé
- MoveIt 2 installé

```bash
# ROS 2 Humble (Ubuntu 22.04)
sudo apt install ros-humble-moveit ros-humble-xacro \
     ros-humble-joint-state-publisher-gui \
     ros-humble-robot-state-publisher
```

### Cloner et compiler

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/<votre-username>/robot_arm_ros2.git .

cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

---

## 5. Commandes de lancement

### Visualisation RViz 2 (avec joint_state_publisher_gui)

```bash
source ~/ros2_ws/install/setup.bash
ros2 launch robot_arm_description display.launch.py
```

> Déplacez les curseurs dans la fenêtre **Joint State Publisher** pour animer chaque articulation.

### Démo MoveIt 2 (planification de trajectoires)

```bash
source ~/ros2_ws/install/setup.bash
ros2 launch robot_arm_moveit_config demo.launch.py
```

> Dans RViz, sélectionnez le groupe **arm**, fixez une pose cible avec la sphère interactive, puis cliquez **Plan & Execute**.

### Vérification de l'arbre TF

```bash
ros2 run tf2_tools view_frames
# Ouvre frames.pdf avec l'arbre complet
evince frames.pdf
```

---

## 6. Captures d'écran

> Remplacez les blocs ci-dessous par vos propres captures après lancement.

### RViz 2 — Modèle visuel

![RViz model](docs/screenshots/rviz_model.png)

*Vue du bras avec les meshes STL, affichage TF, aucun avertissement.*

### RViz 2 — Représentation des collisions

![Collision shapes](docs/screenshots/rviz_collision.png)

*Géométries de collision simplifiées (cylindres et boîtes) activées dans RViz (RobotModel → Collision Enabled).*

### MoveIt 2 — Planification de trajectoire

![MoveIt planning](docs/screenshots/moveit_planning.png)

*Planification RRTConnect entre la pose home et une pose cible, trajectoire affichée en orange.*

---

## 7. Difficultés rencontrées et solutions

| Difficulté | Solution apportée |
|------------|-------------------|
| **Meshes trop grandes** | Application du `scale="0.01 0.01 0.01"` sur chaque `<mesh>` dans les balises `<visual>` |
| **Orientations des meshes incorrectes** | Utilisation des valeurs `rpy` fournies dans le sujet (`${PI/2}`, `-${PI/2}`, etc.) |
| **joint5 (gripper_left) ne suivait pas joint4** | Ajout de la balise `<mimic joint="joint4" multiplier="-1"/>` dans la définition du joint |
| **Fixed frame TF manquant** | Ajout d'un lien `world` et d'un joint `world_fixed` de type `fixed` reliant `world` à `base_link` |
| **MoveIt Setup Assistant — SRDF** | Création manuelle du SRDF avec désactivation des collisions entre liens adjacents |
| **Solveur IK** | KDLKinematicsPlugin suffisant pour 4 DDL ; pas besoin de IKFast pour ce bras |

---

## Structure du dépôt

```
robot_arm_ros2/
├── robot_arm_description/
│   ├── urdf/
│   │   └── robot_arm.urdf.xacro       ← Description complète du robot
│   ├── meshes/
│   │   ├── basement.stl
│   │   ├── base_plate.stl
│   │   ├── forward_drive_arm.stl
│   │   ├── horizontal_arm.stl
│   │   ├── claw_support.stl
│   │   ├── right_finger.stl
│   │   ├── left_finger.stl
│   │   └── ...
│   ├── launch/
│   │   └── display.launch.py          ← RViz 2 + joint_state_publisher_gui
│   ├── config/
│   │   └── robot_arm.rviz             ← Configuration RViz
│   ├── package.xml
│   └── CMakeLists.txt
├── robot_arm_moveit_config/
│   ├── config/
│   │   ├── robot_arm.srdf             ← Groupes cinématiques + collisions
│   │   ├── kinematics.yaml            ← Solveur KDL
│   │   ├── joint_limits.yaml          ← Limites articulaires MoveIt
│   │   ├── ompl_planning.yaml         ← Planificateur OMPL / RRTConnect
│   │   └── moveit_controllers.yaml    ← Contrôleurs simulés
│   ├── launch/
│   │   └── demo.launch.py             ← MoveIt 2 + RViz 2
│   ├── package.xml
│   └── CMakeLists.txt
└── README.md
```

---

## Licence

Apache 2.0 — voir `LICENSE`.
